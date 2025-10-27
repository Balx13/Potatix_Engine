import chess
from config import killer_moves, history_heuristic
from transposition_table import store_tt_entry, probe_tt
from move_ordering import order_moves
from quiescence import quiescence
from stop_event import stop_event
from evulate import game_phase

def determine_R(board: chess.Board) -> int:
    gp = game_phase(board)
    if gp == "opening":
        return 3 # 3 vagy 4
    elif gp == "middlegame":
        return 3
    else:
        return 2 # Endgame

def can_do_null_move(board: chess.Board, previous_null_move, depth, R):

    if board.is_check():
        return False

    if previous_null_move:
        return False

    if not depth or depth <= R+2:
        return False

    # zugzwang
    if game_phase(board) == "endgame":
        return False

    return True

def alphabeta(board: chess.Board, maximizing_player: bool, depth: int, alpha: float, beta: float, datas_for_evulate, previous_null_move=False):

    if depth == 0 or board.is_game_over():
        return quiescence(board, maximizing_player, alpha, beta, datas_for_evulate), None

    if stop_event.is_set():
        return 0, None

    tt_val = probe_tt(board, depth, alpha, beta)
    if tt_val is not None:
        return tt_val, None

    best_move = None
    alpha_orig = alpha
    cutoff_occurred = False

    if maximizing_player:
        max_eval = float('-inf')

        R = determine_R(board)
        if can_do_null_move(board, previous_null_move, depth, R):
            board.turn = not board.turn
            score, _   = alphabeta(board, board.turn, depth-1-R, -beta, -beta+1, datas_for_evulate, previous_null_move=True)
            board.turn = not board.turn
            previous_null_move = True
            if score >= beta:
                return score, None

        for move in order_moves(board, board.legal_moves, depth, datas_for_evulate):
            if stop_event.is_set():
                return 0, None
            board.push(move)
            eval_core, _ = alphabeta(board, False, depth - 1, alpha, beta, datas_for_evulate, previous_null_move=previous_null_move)
            board.pop()
            if eval_core > max_eval:
                max_eval  = eval_core
                best_move = move
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                cutoff_occurred = True
                break

        # TT mentés
        if max_eval <= alpha_orig:
            flag = 'UPPER'
        elif max_eval >= beta:
            flag = 'LOWER'
        else:
            flag = 'EXACT'
        store_tt_entry(board, max_eval, depth, flag)

        if cutoff_occurred:
            if best_move not in killer_moves[depth]:
                if len(killer_moves[depth]) >= 3:
                    killer_moves[depth].pop(0)
                killer_moves[depth].append(best_move)

            board.push(best_move)
            is_check = board.is_check()
            board.pop()
            is_capture = board.is_capture(best_move)
            if not is_check and not is_capture:
                piece = board.piece_at(best_move.from_square)
                piece_type = piece.piece_type
                history_heuristic[piece_type][best_move.from_square][best_move.to_square] += depth * depth

        return max_eval, best_move
    else:
        min_eval = float('inf')

        R = determine_R(board)
        if can_do_null_move(board, previous_null_move, depth, R):
            board.turn = not board.turn
            score, _   = alphabeta(board, board.turn, depth-1-R, -alpha-1, -alpha, datas_for_evulate, previous_null_move=True)
            board.turn = not board.turn
            previous_null_move = True
            if score <= alpha:
                return score, None

        for move in order_moves(board, board.legal_moves, depth, datas_for_evulate):
            if stop_event.is_set():
                return 0, None

            board.push(move)
            eval_core, _ = alphabeta(board, True, depth - 1, alpha, beta, datas_for_evulate,  previous_null_move=previous_null_move)
            board.pop()
            if eval_core < min_eval:
                min_eval  = eval_core
                best_move = move
            beta = min(beta, min_eval)
            if beta <= alpha:
                break

        # TT mentés
        if min_eval <= alpha_orig:
            flag = 'UPPER'
        elif min_eval >= beta:
            flag = 'LOWER'
        else:
            flag = 'EXACT'
        store_tt_entry(board, min_eval, depth, flag)

        if cutoff_occurred:
            if best_move not in killer_moves[depth]:
                if len(killer_moves[depth]) >= 3:
                    killer_moves[depth].pop(0)
                killer_moves[depth].append(best_move)
            board.push(best_move)
            is_check = board.is_check()
            board.pop()
            is_capture = board.is_capture(best_move)
            if not is_check and not is_capture:
                piece = board.piece_at(best_move.from_sq)
                piece_type = piece.piece_type
                history_heuristic[piece_type][best_move.from_sq][best_move.to_sq] += depth * depth

        return min_eval, best_move
