import chess

from transposition_table import transposition_table
from search import alphabeta
from config import board, MAX_DEPTH, killer_moves
import threading
from stop_flag import stop_flag

board = chess.Board()
search_thread = threading.Thread()

def search_worker(max_depth_):
    best_move = None

    for depth in range(1, max_depth_ + 1):
        if stop_flag.stop:
            break
        eval_score_, current_best_move = alphabeta(board, board.turn, depth, float('-inf'), float('inf'))
        if current_best_move:
            best_move = current_best_move
        print(f"info depth {depth} score cp {eval_score_} pv {best_move}", flush=True)

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
                    wtime = float(args[wtime_index+1])
                    btime = float(args[btime_index + 1])

                    winc = 0
                    binc = 0
                    moves_to_go = None
                    if "winc" in args:
                        winc_index = args.index("winc")
                        binc_index = args.index("binc")
                        winc = float(args[winc_index+1])
                        binc = float(args[binc_index + 1])
                        if "moves_to_go" in args:
                            moves_to_go_index = args.index("moves_to_go")
                            moves_to_go = float(args[moves_to_go_index+1])

        elif args[0] == "stop":
            stop_flag.stop = True

    except IndexError:
        continue



