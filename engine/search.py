import chess
from config import killer_moves
from transposition_table import store_tt_entry, probe_tt
from move_ordering import order_moves
from quiescence import quiescence
from stop_event import stop_event

# Minimax alfa-béta vágással
def alphabeta(board: chess.Board, maximizing_player: bool, depth: int, alpha: float, beta: float, datas_for_evulate):
    #maximizing_player = board.turn

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
        for move in order_moves(board, board.legal_moves, depth, datas_for_evulate):
            if stop_event.is_set():
                return 0, None
            board.push(move)
            eval_core, _ = alphabeta(board, False, depth - 1, alpha, beta, datas_for_evulate)
            board.pop()
            if eval_core > max_eval:
                max_eval = eval_core
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

        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in order_moves(board, board.legal_moves, depth, datas_for_evulate):
            if stop_event.is_set():
                return 0, None

            board.push(move)
            eval_core, _ = alphabeta(board, True, depth - 1, alpha, beta, datas_for_evulate)
            board.pop()
            if eval_core < min_eval:
                min_eval = eval_core
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

        return min_eval, best_move
