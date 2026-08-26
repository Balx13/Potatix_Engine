"""
This file is part of Potatix Engine
Copyright (C) 2025-2026 Balázs André

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import random
import chess
import sys
import evaluate
import math

import styles
import transposition_table as tt
from search import alphabeta
import config
import threading
import time
from time_manager import time_for_move
from config import stop_event
from files import read_opening_book

board = chess.Board(chess.STARTING_FEN)
search_thread = threading.Thread()


def timer_worker(time_limit_sec) -> None:
    start = time.time()
    while not stop_event.is_set():
        elapsed = time.time() - start
        if elapsed >= time_limit_sec:
            stop_event.set()
            break
        time.sleep(0.001) # 1ms

def search_worker(max_depth_, wtime_=None, btime_=None, winc_=0, binc_=0, movestogo=None, multipv=1, all_root=False):
    if evaluate.game_phase(board) == "opening" or board.halfmove_clock <= 20:
        opening_move = read_opening_book(board.fen())
        if opening_move is not None:
            print(f"bestmove {opening_move}", flush=True)
            return

    root_turn = board.turn
    stop_event.clear()
    best_move = None
    best_eval = 0.0
    top_moves = []

    if board.turn and wtime_ is not None:
        time_limit_sec = time_for_move(board, wtime_, winc_, movestogo)
    elif not board.turn and btime_ is not None:
        time_limit_sec = time_for_move(board, btime_, binc_, movestogo)
    else:
        time_limit_sec = None

    timer_thread = None
    if time_limit_sec is not None:
        timer_thread = threading.Thread(target=timer_worker, args=(time_limit_sec,))
        timer_thread.start()
    config.engine_turn = board.turn

    for depth in range(1, max_depth_ + 1):
        if stop_event.is_set():
            break
        start_tm = time.time()
        if all_root: # Go depth X
            best_eval_local = float('-inf') if board.turn else float('inf')
            best_move_local = None
            for move in board.legal_moves:
                board.push(move)
                eval_score_, _ = alphabeta(
                    board=board,
                    depth=depth - 1,
                    alpha=float('-inf'),
                    beta=float('inf'),
                    previous_null_move=False)
                board.pop()
                if (board.turn and eval_score_ > best_eval_local) or \
                        (not board.turn and eval_score_ < best_eval_local):
                    best_eval_local = eval_score_
                    best_move_local = move
            eval_score_, current_best_move = best_eval_local, best_move_local
        elif multipv > 1: # MuptiPV
            move_scores = []
            for move in board.legal_moves:
                board.push(move)
                eval_score, _ = alphabeta(
                    board=board,
                    depth=depth - 1,
                    alpha=float('-inf'),
                    beta=float('inf'),
                    previous_null_move=False
                )
                board.pop()
                move_scores.append((eval_score, move))
            move_scores.sort(reverse=not root_turn, key=lambda x: x[0])
            num_legal = len(list(board.legal_moves))
            effective_multipv = min(multipv, num_legal)
            top_moves = move_scores[:effective_multipv]
            current_best_move = top_moves[0][1]
            eval_score_ = top_moves[0][0]
        else: # Normál
            eval_score_, current_best_move = alphabeta(
                board=board,
                depth=depth,
                alpha=float('-inf'),
                beta=float('inf'),
                previous_null_move=False)

        end_tm = time.time()
        elasped_tm = end_tm - start_tm
        nps = config.nodes / elasped_tm if elasped_tm > 0 else 0
        nps = math.trunc(nps)
        elasped_tm = math.trunc(elasped_tm * 10**4) /10**4

        if current_best_move:
            best_move = current_best_move
            best_eval = eval_score_


        if multipv <= 1: # Ha nincs MultiPV
            if abs(best_eval) > 100_000: # Van matt
                mate_in_plies = max(0, 1_000_000 - abs(best_eval))
                mate_in_moves = (mate_in_plies + 1) // 2
                mate_in_moves = mate_in_moves if best_eval > 0 else -mate_in_moves
                print(
        f"info depth {depth} score mate {mate_in_moves} nodes {config.nodes} time {elasped_tm} nps {nps} pv {best_move}"
                )
            else: # Nincs matt
                print(
        f"info depth {depth} score cp {best_eval} nodes {config.nodes} time {elasped_tm} nps {nps} pv {best_move}"
                )
        else: # Van MultiPV
            for idx, (score, move) in enumerate(top_moves):
                if abs(score) > 100_000:
                    mate_in_plies = max(0, 1_000_000 - abs(score))
                    mate_in_moves = (mate_in_plies + 1) // 2
                    mate_in_moves = -mate_in_moves if (config.engine_turn != (lambda x: x > 0)(best_eval)) else mate_in_moves
                    print(f"info depth {depth} score mate {mate_in_moves} multipv {idx+1} nodes {config.nodes} time {elasped_tm} nps {nps} pv {move}")
                else:
                    print(f"info depth {depth} score cp {score} multipv {idx+1} nodes {config.nodes} time {elasped_tm} nps {nps} pv {move}")
        config.nodes = 0 # Reset

    if timer_thread is not None:
        timer_thread.join()
    stop_event.clear()

    if best_move:
        print(f"bestmove {best_move}", flush=True)
    else:
        legal_moves = list(board.legal_moves)

        fallback_move = random.choice(legal_moves) if legal_moves else None
        print(f"bestmove {fallback_move}", flush=True)

def read_console():
    try:
        return input().strip().split()
    except EOFError:
        return [""]

def send_command(args=None):
    if args is None:
        args = read_console()
    if args != [""]:
        uci(args)

def setoption(args) -> None:
    name_index = args.index("name")
    value_index = args.index("value")
    if args[name_index + 1] == "MaxDepth":
        try:
            value = int(args[value_index + 1])
        except (IndexError, ValueError):
            print("info string Error: invalid value for MaxDepth", flush=True)
            return
        if 1 <= value <= 100_000:
            config.MAX_DEPTH = value
            config.killer_moves = [[] for _ in range(config.MAX_DEPTH + 1)]
        else:
            print("info string Error: the value is too large or too small", flush=True)
            return
    elif args[name_index + 1] == "TTSize":
        value = int(args[value_index + 1])
        if 1 <= value <= 100_000_000:
            tt.Max_tt_size = value
        else:
            print("info string Error: the value is too large or too small", flush=True)
            return
    elif args[name_index+1] == "MultiPV":
        value = int(args[value_index + 1])
        if 1 <= value <= 64:
            config.multipv = value
        else:
            print("info string Error: the value is too large or too small", flush=True)
            return
    elif args[name_index+1] == "GameStyle":
        value = args[value_index+1]
        if value in tuple(config.styles.keys()):
            config.chosen_style = value
        else:
            print("info string Error: The value is not an existing style", flush=True)


def go(args) -> None:
    global search_thread
    if search_thread and search_thread.is_alive():
        stop_event.set()
        search_thread.join()
    stop_event.clear()

    if len(args) == 1:
        search_thread = threading.Thread(
            target=search_worker,
            args=(config.MAX_DEPTH,),
            kwargs={"multipv": config.multipv})
        search_thread.start()
    elif len(args) == 3 and args[1] == "depth":
        search_thread = threading.Thread(
            target=search_worker,
            args=(int(args[2]),),
            kwargs={"all_root": True, "multipv": config.multipv})
        search_thread.start()
    elif len(args) == 3 and args[1] == "movetime":
        movetime_index = args.index("movetime")
        movetime = float(args[movetime_index + 1]) / 1000
        search_thread = threading.Thread(
            target=search_worker,
            args=(config.MAX_DEPTH, movetime, movetime, 0, 0, 1),
            kwargs={"multipv": config.multipv})
        search_thread.start()
    elif len(args) > 4:
        if "wtime" in args:  # ha már van wtime, akkor biztos, hogy kapunk időt
            wtime_index = args.index("wtime")
            btime_index = args.index("btime")
            wtime = float(args[wtime_index + 1]) / 1000
            btime = float(args[btime_index + 1]) / 1000

            winc = 0
            binc = 0
            movestogo = None
            if "winc" in args:
                winc_index = args.index("winc")
                binc_index = args.index("binc")
                winc = float(args[winc_index + 1]) / 1000
                binc = float(args[binc_index + 1]) / 1000
                # UCI uses 'movestogo' (no underscore)
                if "movestogo" in args:
                    movestogo_index = args.index("movestogo")
                    movestogo = float(args[movestogo_index + 1])
            search_thread = threading.Thread(
                target=search_worker,
                args=(config.MAX_DEPTH, wtime, btime, winc, binc, movestogo),
                kwargs = {"multipv": config.multipv}
            )
            search_thread.start()

def position(args: list) -> None:
    global board
    if args[1] == "startpos":
        board = chess.Board(chess.STARTING_FEN)
        if "moves" in args:
            for move in args[3:]:
                board.push_uci(move)
    elif args[1] == "fen":
        if "moves" in args:
            moves_index = args.index("moves")
            board = chess.Board(" ".join(args[2:moves_index]))
            for move in args[moves_index + 1:]:
                board.push_uci(move)
        else:
            board = chess.Board(" ".join(args[2:]))

def reset() -> None:
    global board
    if search_thread and search_thread.is_alive():  # leállítjuk a keresést, ha a GUI nem tette meg
        stop_event.set()
        search_thread.join()
    stop_event.clear()

    board = chess.Board()
    config.nodes = 0
    config.engine_turn = True

    tt.transposition_table.clear()

    for km in config.killer_moves:
        km.clear()

    for piece_type in range(6):
        for from_sq in range(64):
            for to_sq in range(64):
                config.history_heuristic[piece_type][from_sq][to_sq] = 0

def uci(args):
    global search_thread, board
    try:
        match args[0]:
            case "uci":
                print("id name Potatix Engine", flush=True)
                print("id author Balazs Andre", flush=True)

                print(f"option name MultiPV type spin default {config.multipv} min 1 max 64", flush=True)
                print(f"option name MaxDepth type spin default {config.MAX_DEPTH} min 1 max 100000", flush=True)
                print(f"option name TTSize type spin default {tt.Max_tt_size} min 1 max 100000000", flush=True)
                print(f"option name GameStyle type combo default {config.chosen_style}{
                    styles.available_styles_to_string()}", flush=True)

                print("uciok", flush=True)
            case "isready":
                print("readyok", flush=True)
            case "ucinewgame":
                reset()
            case "quit":
                sys.exit()
            case "position":
                position(args)
            case "go":
                go(args)
            case "setoption":
                setoption(args)
            case "stop":
                stop_event.set()
            case _:
                print(f"info string Error: unknown command \"{' '.join(args)}\"", flush=True)
    except IndexError:
        return None
    except Exception as e:
        print(f"info string Error: \"{e}\"", flush=True)
        return None
