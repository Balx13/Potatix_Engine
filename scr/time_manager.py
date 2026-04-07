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


def estimate_moves_to_go(board: chess.Board) -> int:
    fullmove = board.fullmove_number
    estimated_moves_to_go = max(15, 45 - fullmove)
    piece_count = len(board.piece_map())
    if piece_count <= 6:
        estimated_moves_to_go = max(estimated_moves_to_go, 20)
    return estimated_moves_to_go


def estimate_time_for_move(board: chess.Board, time_left: float, increment: float, moves_to_go) -> float:
    if moves_to_go is None:
        moves_to_go = estimate_moves_to_go(board)
    allocated_time = min(time_left / moves_to_go + increment, time_left / 1.5 - 1)
    return max(0.05, allocated_time)
