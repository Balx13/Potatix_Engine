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
import config
import evaluate
from stop_event import stop_event
from move_ordering import order_moves
from quiescence import quiescence
from transposition_table import store_tt_entry, probe_tt


def get_adaptive_bonus(board, move: chess.Move) -> float:
    board.push(move)
    white_m = config.multipliers["engine"]
    black_m = config.multipliers["oppoment"]
    if not config.engine_turn:
        white_m, black_m = black_m, white_m

    bonus = 0
    phase = evaluate.game_phase(board)
    w = config.tapered_weights[phase]
    mobility_score = evaluate.eval_mobility(board) * w["mobility"]
    king_safety_score = evaluate.eval_king_safety(board) * w["king_safety"]
    bishop_pair_score = evaluate.eval_bishop_pair(board) * w["bishop_pair"]
    rook_open_files_score = evaluate.eval_rook_open_files(board) * w["rook_files"]

    def calculate_component(score, wm_val, bm_val):
        if score == 0: return 0
        m = wm_val if score > 0 else bm_val

        return score * (m - 1.0)

    # Alkalmazzuk a komponensekre
    bonus += calculate_component(mobility_score, white_m["mobility"], black_m["mobility"])
    bonus += calculate_component(king_safety_score, white_m["king_safety"], black_m["king_safety"])
    bonus += calculate_component(rook_open_files_score, white_m["rook_op_files"], black_m["rook_op_files"])
    bonus += calculate_component(bishop_pair_score, white_m["bishop_pairs"], black_m["bishop_pairs"])

    bonus = max(-60, min(60, bonus))
    board.pop()
    return bonus
    


def determine_R(depth) -> int:
    # Meghatározza, hogy az LMR mennyivel sekélyebben keressen

    return 1 + (depth // 5)

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

    # A fő kereső függvény

    if depth <= 0 or board.is_game_over():
        color = 1 if board.turn == chess.WHITE else -1
        return color * quiescence(board, alpha, beta, ply), None
    if board.is_repetition(2) or board.halfmove_clock >= 100:
        return 0, None  # Döntetlen értékelése

    if stop_event.is_set():
        return 0, None

    tt_val = probe_tt(board, depth, alpha, beta)
    if tt_val is not None:
        return tt_val, None

    best_move = None
    alpha_orig = alpha
    cutoff_occurred = False
    max_eval = float('-inf')
    R = determine_R(depth)
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
            previous_null_move=True
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
                previous_null_move=True
            )
            eval_score = -score
            if eval_score == -0.0:
                eval_score = 0.0
        board.pop()

        if (ply == 0
            and move is not None # Adaptív összehasonlítás csak a rootban
            and best_move is not None # Ha van best_move
            and config.adaptive_mode # Ha engedélyezett az adaptív mód
        ):
            adaptive_eval_score = eval_score + get_adaptive_bonus(board, move)
            adaptive_max_eval = max_eval + get_adaptive_bonus(board, best_move)
            if adaptive_eval_score > adaptive_max_eval:
                max_eval = eval_score
                best_move = move
        else:
            if eval_score > max_eval:
                max_eval  = eval_score
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

                history_index += depth * depth
                if history_index > 100:
                    history_index = 100
                    config.history_heuristic[piece_type-1]\
                    [best_move.from_square][best_move.to_square] = history_index

    return max_eval, best_move
