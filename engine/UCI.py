"""
This file is part of Potatix Engine
Copyright (C) 2025 Balázs André
Potatix Engine is licensed under a CUSTOM REDISTRIBUTION LICENSE (see LICENCE.txt)
"""

import json
import random
import chess
import sys
import transposition_table as tt
from evulate import game_phase
from search import alphabeta
import config
import threading
import time
from pathlib import Path
from time_manager import estimate_time_for_move
from stop_event import stop_event
from adaptive_style import playing_style_recognition
from evulate import evaluate

board = config.board
MAX_DEPTH = config.MAX_DEPTH
killer_moves = config.killer_moves
history_heuristic = config.history_heuristic
search_thread = threading.Thread()

transposition_table_ = tt.transposition_table
Max_tt_size = tt.Max_tt_size

def is_in_opening_book(board_fen):
    if getattr(sys, 'frozen', False):
        # PyInstaller futás közben
        BASE_DIR = Path(sys._MEIPASS) / "engine"
    else:
        # normál futás
        BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR / "data" / "opening_book.jsonl"
    with open(file_path, "r", encoding="utf-8") as f:
        for position in f:
            data = json.loads(position)
            fen = data["fen"]
            moves = [m["move"] for m in data["top_moves"]]
            if fen == board_fen:
                return random.choice(moves)
        return None

def timer_worker(time_limit_sec):
    # Számolja az eltelt időt

    start = time.time()
    while not stop_event.is_set():
        elapsed = time.time() - start
        if elapsed >= time_limit_sec:
            stop_event.set()
            break
        time.sleep(0.001)  # kis várakozás, hogy ne terhelje a CPU-t

def search_worker(max_depth_, wtime_=None, btime_=None, winc_=0, binc_=0, movestogo=None, forced_child=False):
    # Ez indítja el és kezeli a keresést

    if game_phase(board) == "opening":
        # Csak megnyitásban keres megnyitási könyvet (így végjátékban nem néz át 25 000 állást)
        opening_move = is_in_opening_book(board.fen())
        if opening_move is not None:
            print(f"bestmove {opening_move}", flush=True)
            return

    transposition_table_.clear()
    stop_event.clear()
    best_move = None

    if board.turn and wtime_ is not None:
        time_limit_sec = estimate_time_for_move(board, wtime_, winc_, movestogo)
    elif not board.turn and btime_ is not None:
        time_limit_sec = estimate_time_for_move(board, btime_, binc_, movestogo)
    else:
        time_limit_sec = None

    timer_thread = None
    if time_limit_sec is not None:
        timer_thread = threading.Thread(target=timer_worker, args=(time_limit_sec,))
        timer_thread.start()

    start_board = chess.Board(chess.STARTING_FEN)
    diff_count = sum(1 for sq in chess.SQUARES if start_board.piece_at(sq) != board.piece_at(sq))

    if diff_count >= 20:
        adaptive_mode = True
    else:
        adaptive_mode = False

    best_eval_instability = 0.0
    danger_score = 0.0
    second_best_eval = None

    """
    A danger_score egy veszélyességi pontszám: minnél nagyobb, annál kevesebb cutoff
    a horizon-effektus elkerülése végett
    """

    for depth in range(1, max_depth_ + 1):
        if stop_event.is_set():
            break

        if forced_child:
            best_eval_local = float('-inf') if board.turn else float('inf')
            best_move_local = None
            for move in board.legal_moves:
                board.push(move)
                eval_score_, _ = alphabeta(
                    board=board,
                    maximizing_player=board.turn,
                    depth=depth-1,
                    alpha=float('-inf'),
                    beta=float('inf'),
                    previous_null_move=False,
                    danger_score=danger_score)
                board.pop()
                if (board.turn and eval_score_ > best_eval_local) or \
               (not board.turn and eval_score_ < best_eval_local):
                    best_eval_local = eval_score_
                    best_move_local = move
            eval_score_, current_best_move = best_eval_local, best_move_local
        else:
            eval_score_, current_best_move = alphabeta(
                board=board,
                maximizing_player=board.turn,
                depth=depth,
                alpha=float('-inf'),
                beta=float('inf'),
                previous_null_move=False,
                danger_score=danger_score)

        if current_best_move:
            best_move = current_best_move
            best_eval = eval_score_
            if second_best_eval is not None:
                best_eval_instability = abs(best_eval-second_best_eval)

                # A 20.5 az az ingadozás, ami a páratlan-páros depth-eknél jön ki,
                # ezért a danger_score stabilizálása érdekében levonjuk
                best_eval_instability = min(50, best_eval_instability/4)-20.5
            second_best_eval = eval_score_

        danger_score = best_eval_instability

        print(f"info depth {depth} score cp {eval_score_} pv {best_move}", flush=True)

    if timer_thread is not None:
        timer_thread.join()
    stop_event.clear()

    if best_move:
        print(f"bestmove {best_move}", flush=True)
    else:
        legal_moves = list(board.legal_moves)
        fallback_move = legal_moves[0] if legal_moves else None
        print(f"bestmove {fallback_move}", flush=True)


def read_cmd():
    # Kiolvassa a konzolból a parancsokat

    args = [""]
    try:
        line = input().strip()
        args = line.split()
        return args
    except EOFError:
        return args
    except:
        return args

def send_cmd(args=None):
    # Elküldi a parancsokat az UCI-nek
    if args is None:
        args = read_cmd()
    if args != [""]:
        info_ = UCI(args)

        if info_ == "quit":
            return "quit"
    return None

def UCI(args):
    # Ez kezeli az UCI protokollt

    global search_thread, killer_moves, board, Max_tt_size, MAX_DEPTH
    try:
        if args[0] == "uci":
            print("id name Potatix Engine", flush=True)
            print("id author Balazs Andre", flush=True)

            print("option name MaxDepth type spin default 50 min 1 max 100", flush=True)
            print("option name TTSize type spin default 1000000 min 1 max 100000000", flush=True)

            print("uciok", flush=True)
        elif args[0] == "isready":
            print("readyok", flush=True)
        elif args[0] == "ucinewgame":
            if search_thread and search_thread.is_alive(): # leállítjuk a keresést, ha a GUI nem tette meg
                stop_event.set()
                search_thread.join()
            stop_event.clear()

            board = chess.Board()
            transposition_table_.clear()

            for km in killer_moves:
                km.clear()

            for piece_type in range(6):
                for from_sq in range(64):
                    for to_sq in range(64):
                        history_heuristic[piece_type][from_sq][to_sq] = 0

        elif args[0] == "quit":
            if search_thread and search_thread.is_alive():
                stop_event.set()
                search_thread.join()

            stop_event.clear()
            return "quit"

        elif args[0] == "position":
            if  args[1] == "startpos":
                board = chess.Board(chess.STARTING_FEN)
                if len(args) > 2:
                    for move in args[3:]:
                        board.push_uci(move)
            elif args[1] == "fen":
                if "moves" in args:
                    moves_index = args.index("moves")
                    board = chess.Board(" ".join(args[2:moves_index]))
                    for move in args[moves_index+1:]:
                        board.push_uci(move)
                else:
                    board = chess.Board(" ".join(args[2:]))

        elif args[0] == "go":
            if search_thread and search_thread.is_alive():
                stop_event.set()
                search_thread.join()
            stop_event.clear()

            if len(args) == 1:
                search_thread = threading.Thread(target=search_worker, args=(MAX_DEPTH,))
                search_thread.start()
            elif len(args) == 3 and args[1] == "depth":
                search_thread = threading.Thread(target=search_worker, args=(int(args[2]),), kwargs={"forced_child": True})
                search_thread.start()
            elif len(args) == 3 and args[1] == "movetime":
                movetime_index = args.index("movetime")
                movetime = float(args[movetime_index+1]) / 1000
                search_thread = threading.Thread(target=search_worker, args=(MAX_DEPTH, movetime, movetime, 0, 0, 1))
                search_thread.start()
            elif len(args) > 4:
                if "wtime" in args: # ha már van wtime, akkor biztos, hogy kapunk időt
                    wtime_index = args.index("wtime")
                    btime_index = args.index("btime")
                    wtime = float(args[wtime_index+1]) / 1000
                    btime = float(args[btime_index + 1]) / 1000

                    winc = 0
                    binc = 0
                    moves_to_go = None
                    if "winc" in args:
                        winc_index = args.index("winc")
                        binc_index = args.index("binc")
                        winc = float(args[winc_index+1]) / 1000
                        binc = float(args[binc_index + 1]) / 1000
                        if "moves_to_go" in args:
                            moves_to_go_index = args.index("moves_to_go")
                            moves_to_go = float(args[moves_to_go_index+1])
                    search_thread = threading.Thread(
                        target=search_worker,
                        args=(MAX_DEPTH, wtime, btime, winc, binc, moves_to_go)
                    )
                    search_thread.start()
        elif args[0] == "setoption":
            name_index = args.index("name")
            value_index = args.index("value")
            if args[name_index+1] == "MaxDepth":
                MAX_DEPTH = int(args[value_index+1])
                killer_moves = [[] for _ in range(MAX_DEPTH)]
            elif args[name_index+1] == "TTSize":
                value_num= int(args[value_index+1])
                if 1 <= value_num <= 100_000_000:
                    Max_tt_size *= 0
                    Max_tt_size += value_num

        elif args[0] == "stop":
            stop_event.set()

        else:
            print(f"info string Error: unknown command \"{' '.join(args)}\"", flush=True)

    except IndexError:
        return None
    except Exception as e:
        print(f"info string Error: \"{e}\"", flush=True)
        return None

