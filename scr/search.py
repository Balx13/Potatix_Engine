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
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import chess

import adaptive_style
import config
import evaluate
from config import stop_event
from move_ordering import order_moves
from quiescence import quiescence
from transposition_table import store_tt_entry, probe_tt
    



def can_do_null_move(board: chess.Board, previous_null_move, depth, R):
    # Megmondja, hogy lehet egy Null Move Pruning-ot csinálni vagy nem

    if board.is_check():
        return False

    if previous_null_move:
        return False

    if not depth or depth <= R+2:
        return False

    # zugzwang
    if evaluate.game_phase(board) == "endgame":
        return False

    return True

def alphabeta(
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        ply: int=0,
        previous_null_move: bool=False):

    """
    A fő kereső függvény.
    Negamax-alapú keresés.
    """

    config.nodes += 1

    if board.is_fivefold_repetition() or board.is_seventyfive_moves() or board.is_stalemate() or board.can_claim_draw():
        return 0, None  # Döntetlen
    if depth <= 0 or board.is_game_over():
        return quiescence(board, alpha, beta, ply), None

    if stop_event.is_set():
        return 0, None

    tt_val = probe_tt(board, depth, alpha, beta)
    if tt_val is not None:
        return tt_val, None

    best_move = None
    alpha_orig = alpha
    cutoff_occurred = False
    max_eval = float('-inf')
    R = 1 + depth // 5
    if can_do_null_move(board, previous_null_move, depth, R):
        board.push(chess.Move.null())
        score, _ = alphabeta(
            board=board,
            depth=max(0, depth-1-R),
            alpha=-beta,
            beta=-alpha,
            ply=ply + 1,
            previous_null_move=True
        )
        eval_score = -score
        if eval_score == -0.0:
            eval_score = 0.0
        board.pop()
        if eval_score >= beta:
            return eval_score, None

    for move, moves_score in order_moves(board, board.legal_moves, depth):
        reduction = 0
        current_lmr = False

        if stop_event.is_set():
            return 0, None

        if evaluate.game_phase(board) != "opening" and not board.is_check() \
                and not board.is_capture(move) and not board.is_castling(move) and depth <= 3:
            if moves_score < 20 and best_move is not None and depth <= 2: # LMP
                continue
            elif moves_score <= 40: # LMR
                current_lmr = True
                reduction = R

        board.push(move)
        score, _ = alphabeta(
            board=board,
            depth=max(0, depth-1-reduction),
            alpha=-beta,
            beta=-alpha,
            ply=ply + 1,
            previous_null_move=False
        )
        eval_score = -score
        if eval_score == -0.0:
            eval_score = 0.0

        if current_lmr and eval_score > alpha:
            score, _ = alphabeta(
                board=board,
                depth=depth-1,
                alpha=-beta,
                beta=-alpha,
                ply=ply + 1,
                previous_null_move=False
            )
            eval_score = -score
            if eval_score == -0.0:
                eval_score = 0.0
        board.pop()

        if ply == 0 and best_move is not None and config.adaptive_mode:
            opponent_color = not board.turn
            biased_score = eval_score + adaptive_style.get_adaptive_bias(board, move, opponent_color)
            biased_best = max_eval + adaptive_style.get_adaptive_bias(board, best_move, opponent_color)
            if biased_score > biased_best:
                max_eval = eval_score
                best_move = move
        else:
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
        alpha = max(alpha, max_eval)
        if beta <= alpha:
            cutoff_occurred = True
            break

    if not previous_null_move:
        # TT mentés
        if max_eval <= alpha_orig:
            flag = 'UPPER'
        elif max_eval >= beta:
            flag = 'LOWER'
        else:
            flag = 'EXACT'
        store_tt_entry(board, max_eval, depth, flag)

        if cutoff_occurred:
            if depth < len(config.killer_moves):
                if best_move not in config.killer_moves[depth]:
                    if len(config.killer_moves[depth]) >= 3:
                        config.killer_moves[depth].pop(0)
                    config.killer_moves[depth].append(best_move)
            board.push(best_move)
            is_check = board.is_check()
            board.pop()
            is_capture = board.is_capture(best_move)
            if not is_check and not is_capture:
                piece = board.piece_at(best_move.from_square)
                piece_type = piece.piece_type
                history_index = config.history_heuristic[piece_type-1]\
                [best_move.from_square][best_move.to_square]
                history_index = min(100, history_index + depth**2)
                config.history_heuristic[piece_type - 1] \
                    [best_move.from_square][best_move.to_square] = history_index
                config.history_heuristic[piece_type-1]\
                [best_move.from_square][best_move.to_square] = history_index

    return max_eval, best_move
