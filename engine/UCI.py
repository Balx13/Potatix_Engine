import chess
from transposition_table import transposition_table, Max_tt_size
from search import alphabeta
from config import board, MAX_DEPTH, killer_moves
import threading
import time
from time_manager import estimate_time_for_move
from stop_event import stop_event
from adaptive_style import playing_style_recognition
from evulate import evaluate_board

board = chess.Board()

search_thread = None


def timer_worker(time_limit_sec):
    start = time.time()
    while not stop_event.is_set():
        elapsed = time.time() - start
        if elapsed >= time_limit_sec:
            stop_event.set()
            break
        time.sleep(0.001)  # kis várakozás, hogy ne terhelje a CPU-t

def search_worker(max_depth_, wtime=None, btime=None, winc=0, binc=0, movestogo=None):
    transposition_table.clear()
    stop_event.clear()
    best_move = None

    if board.turn and wtime is not None:
        time_limit_sec = estimate_time_for_move(board, wtime, winc, movestogo)
    elif not board.turn and btime is not None:
        time_limit_sec = estimate_time_for_move(board, btime, binc, movestogo)
    else:
        time_limit_sec = None

    timer_thread = None
    if time_limit_sec is not None:
        timer_thread = threading.Thread(target=timer_worker, args=(time_limit_sec,))
        timer_thread.start()

    _, musters = evaluate_board(board, with_muster=True, adaptive_mode=False)
    playing_style = playing_style_recognition(musters=musters, color=not board.turn)
    start_board = chess.Board(chess.STARTING_FEN)
    diff_count = sum(1 for sq in chess.SQUARES if start_board.piece_at(sq) != board.piece_at(sq))

    if diff_count >= 20:
        adaptive_mode = True
    else:
        adaptive_mode = False

    for depth in range(1, max_depth_ + 1):
        if stop_event.is_set():
            break
        eval_score_, current_best_move = alphabeta(board, board.turn, depth, float('-inf'), float('inf'), [playing_style, board.turn, adaptive_mode])
        if current_best_move:
            best_move = current_best_move
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


while True:
    try:
        line = input().strip()
        args = line.split()
    except EOFError:
        continue
    except:
        continue
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
            #tt törlés, új tábla, reset
            if search_thread and search_thread.is_alive(): # leállítjuk a keresést, ha a GUI nem tette meg
                stop_event.set()
                search_thread.join()
            stop_event.clear()

            board = chess.Board()
            transposition_table.clear()
            killer_moves = [[] for _ in range(MAX_DEPTH)]
            opponent_positions = []

        elif args[0] == "quit":
            if search_thread and search_thread.is_alive():
                stop_event.set()
                search_thread.join()

            stop_event.clear()
            break

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
                search_thread = threading.Thread(target=search_worker, args=(int(args[2]),))
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
                    search_thread = threading.Thread(target=search_worker, args=(MAX_DEPTH, wtime, btime, winc, binc, moves_to_go))
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
                    Max_tt_size = value_num

        elif args[0] == "stop":
            stop_event.set()

    except IndexError:
        continue
    except Exception as e:
        print(f"info string Error: \"{e}\"", flush=True)
        # Nincs bestmove, a motor csak vár.
        continue


