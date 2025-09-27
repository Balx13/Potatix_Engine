import chess

from transposition_table import transposition_table
from search import alphabeta
from config import board, MAX_DEPTH, killer_moves
import threading
from stop_flag import stop_flag
import time
from time_manager import estimate_time_for_move

board = chess.Board()
search_thread = threading.Thread()

def timer_worker(time_limit_sec):
    """
    Egyszerű időzítő szál. Ha az idő lejár, beállítja a stop_flag-et.
    """
    start = time.time()
    while not stop_flag.stop:
        elapsed = time.time() - start
        if elapsed >= time_limit_sec:
            stop_flag.stop = True
            break
        time.sleep(0.01)  # kis várakozás, hogy ne terhelje a CPU-t

def search_worker(max_depth_, wtime=None, btime=None, winc=0, binc=0, movestogo=None):
    stop_flag.stop = False
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

    for depth in range(1, max_depth_ + 1):
        if stop_flag.stop:
            break
        eval_score_, current_best_move = alphabeta(board, board.turn, depth, float('-inf'), float('inf'))
        if current_best_move:
            best_move = current_best_move
        print(f"info depth {depth} score cp {eval_score_} pv {best_move}", flush=True)

    if timer_thread is not None:
        timer_thread.join()

    if best_move:
        print(f"bestmove {best_move}", flush=True)
    else:
        legal_moves = list(board.legal_moves)
        fallback_move = legal_moves[0] if legal_moves else None
        print(f"bestmove {fallback_move}", flush=True)
    stop_flag.stop = False


while True:
    try:
        line = input().strip()
        args = line.split()
    except EOFError:
        continue

    try:
        if args[0] == "uci":
            print("id name Adaptix")
            print("id author AndreBalazs")
            print("uciok", flush=True)
        elif args[0] == "isready":
            print("readyok", flush=True)
        elif args[0] == "ucinewgame":
            #tt törlés, új tábla, reset
            if search_thread and search_thread.is_alive(): # leállítjuk a keresést, ha a GUI nem tette meg
                stop_flag.stop = True
                search_thread.join()
            stop_flag.stop = False

            board = chess.Board()
            transposition_table.clear()
            killer_moves = [[] for _ in range(MAX_DEPTH)]


        elif args[0] == "quit":
            if search_thread and search_thread.is_alive():
                stop_flag.stop = True
                search_thread.join()
            break

        elif args[0] == "position":
            if  args[1] == "startpos":
                board = chess.Board(chess.STARTING_FEN)
                if len(args) > 2:
                    for move in args[2:]:
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
                stop_flag.stop = True
                search_thread.join()
            stop_flag.stop = False
            if len(args) == 1:
                search_thread = threading.Thread(target=search_worker, args=(MAX_DEPTH,))
                search_thread.start()
            elif len(args) == 3 and args[1] == "depth":
                search_thread = threading.Thread(target=search_worker, args=(int(args[2]),))
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

        elif args[0] == "stop":
            stop_flag.stop = True

    except IndexError:
        continue


