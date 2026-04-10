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
    if config.spare_time is None:
        config.spare_time = time_left * 0.1 # 10% tartalékidő
    spare_time_l = config.spare_time if time_left > config.spare_time*1.5 else 0 # Ha az idő 15%-át elhasználtuk, felhasználjuk a tartalék időt is
    allocated_time = min(time_left / moves_to_go + increment, time_left / 2) - spare_time_l
    return max(0.05, allocated_time)
