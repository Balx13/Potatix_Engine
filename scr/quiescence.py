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
from move_ordering import order_moves
from evaluate import evaluate
from config import PIECE_VALUES
from stop_event import stop_event

def see(board: chess.Board, move: chess.Move) -> int:

    if not board.is_capture(move):
        return 0

    to_sq = move.to_square
    from_sq = move.from_square

    captured = board.piece_at(to_sq)
    attacker = board.piece_at(from_sq)

    if captured is None or attacker is None:
        return 0

    gain = [PIECE_VALUES[captured.piece_type]]

    board.push(move)

    side = not attacker.color
    depth = 0

    while True:
        attackers = board.attackers(side, to_sq)

        if not attackers:
            break

        least_sq = min(
            attackers,
            key=lambda sq: PIECE_VALUES[board.piece_at(sq).piece_type]
        )

        piece = board.piece_at(least_sq)
        gain.append(
            PIECE_VALUES[piece.piece_type] - gain[depth]
        )

        reply = chess.Move(least_sq, to_sq)
        board.push(reply)

        depth += 1
        side = not side

    for i in range(len(gain) - 2, -1, -1):
        gain[i] = max(gain[i], -gain[i + 1])

    board.pop()
    for _ in range(depth):
        board.pop()

    return gain[0]


def quiescence(board: chess.Board, alpha: float, beta: float, ply) -> float:
    color = 1 if board.turn == chess.WHITE else -1
    stand_pat = evaluate(board, ply) * color

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat
    for move, _ in order_moves(board, board.legal_moves, depth=0):
        if stop_event.is_set():
            return 0
        if not board.is_capture(move):
            continue
        if see(board, move) < 0:
            continue
        board.push(move)
        score = -quiescence(board, -beta, -alpha, ply+1)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha
