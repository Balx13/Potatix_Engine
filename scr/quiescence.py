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
from evaluate import evaluate
from stop_event import stop_event
import config

def mini_local_ordering(board: chess.Board, legal_moves):
    def score(move_):
        piece = board.piece_at(move_.from_square)
        if board.is_capture(move_): # Ütés
            victim = board.piece_at(move_.to_square)
            attacker = piece # piece = board.piece_at(move_.from_square)
            victim_value = config.PIECE_VALUES[victim.piece_type] if victim else 0
            attacker_value = config.PIECE_VALUES[attacker.piece_type] if attacker else 0
            return 1000 + 10 * victim_value - attacker_value
        elif board.is_check(): # Ha nem ütés, akkor sakkban vagyunk, így ez ellen-sakk
            return 10
        return 0
    return sorted(legal_moves, key=score, reverse=True)


def get_smallest_attacker(board: chess.Board, square, color, occupied):
    attackers_mask = board.attackers_mask(color, square, occupied)
    if not attackers_mask:
        return None
    for piece_type in (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING):
        type_mask = int(board.pieces_mask(piece_type, color)) & occupied
        subset = attackers_mask & type_mask
        if subset:
            return (subset & -subset).bit_length() - 1
    return None


def see(board: chess.Board, move: chess.Move) -> int:
    to_sq = move.to_square
    from_sq = move.from_square
    def get_val(p_type):
        return config.PIECE_VALUES.get(p_type, 0)

    captured_piece = board.piece_at(to_sq)
    gain = [0] * 33
    gain[0] = get_val(captured_piece.piece_type) if captured_piece else 0
    attacker_type = board.piece_at(from_sq).piece_type
    occupied = board.occupied
    occupied &= ~(1 << from_sq)
    current_color = not board.turn
    depth = 0

    while True:
        depth += 1
        attacker_sq = get_smallest_attacker(board, to_sq, current_color, occupied)
        if attacker_sq is None:
            break
        gain[depth] = get_val(attacker_type) - gain[depth - 1]
        attacker_type = board.piece_at(attacker_sq).piece_type
        occupied &= ~(1 << attacker_sq)  # Ő is elhagyja a helyét
        current_color = not current_color
    while depth > 0:
        gain[depth - 1] = -max(-gain[depth - 1], gain[depth])
        depth -= 1
    return gain[0]


def quiescence(board: chess.Board, alpha: float, beta: float, ply: int) -> float:

    if stop_event.is_set():
        return 0
    is_check = board.is_check()
    if not is_check:
        stand_pat = evaluate(board, ply)
        if not board.turn:  # Sötét jön
            stand_pat = -stand_pat
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
        legal_moves = board.generate_legal_captures()
    else:
        legal_moves = board.legal_moves # Ha sakk van, akkor az összes legális lépés védi

    if board.is_fivefold_repetition() or board.is_seventyfive_moves() or board.is_stalemate() or board.can_claim_draw():
        return 0.0  # Döntetlen
    elif board.is_game_over():
        ev = evaluate(board, ply)
        return ev if board.turn else -ev

    for move in mini_local_ordering(board, legal_moves):
        if stop_event.is_set():
            return 0
        if not is_check: # Sakknál nincs see
            if see(board, move) < 0: # See megfogta
                continue
        board.push(move)
        score = -quiescence(board, -beta, -alpha, ply+1)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha