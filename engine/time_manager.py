"""
This file is part of Potatix Engine
Copyright (C) 2025-2026 Balázs André
Potatix Engine is licensed under a CUSTOM REDISTRIBUTION LICENSE (see LICENCE.txt)
"""
from evulate import eval_king_safety
import chess
from config import PIECE_VALUES


def estimate_moves_to_go(board: chess.Board) -> int:
    # Megbecsli a moves_to_go-t

    piece_count = len(board.piece_map())
    moves_based_on_material = max(5, piece_count // 2)

    fullmove = board.fullmove_number
    if fullmove < 15:
        phase_factor = 1.5
    elif fullmove < 30:
        phase_factor = 1.0
    else:
        phase_factor = 0.7

    estimated_moves_to_go = max(5, int(moves_based_on_material * phase_factor))
    estimated_moves_to_go = min(60, estimated_moves_to_go)

    return estimated_moves_to_go


def estimate_time_for_move(board: chess.Board, base_time: float, increment: float, moves_to_go=None) -> float:
    # Megbecsli, hogy az adott lépésre mennyi időt érdemes szánni

    move_number = board.fullmove_number
    if move_number < 15:
        phase_factor = 0.85
    elif move_number < 40:
        phase_factor = 1.0
    else:
        phase_factor = 1.1

    material_balance = 0

    for piece_type, value in PIECE_VALUES.items():
        material_balance += len(board.pieces(piece_type, chess.WHITE)) * value
        material_balance -= len(board.pieces(piece_type, chess.BLACK)) * value

    complexity_factor = 1.0
    if abs(material_balance) <= 2:  # kiegyenlített pozíció
        complexity_factor += 0.05
    if eval_king_safety(board) > 5:
        complexity_factor += 0.2  # sakk / támadás

    if moves_to_go is None:
        moves_to_go = estimate_moves_to_go(board)
    base_allocation = (base_time / moves_to_go) + increment

    max_allocation = base_time * 0.4  # 40%
    min_allocation = base_time * 0.05  # 5%

    allocated_time = base_allocation * phase_factor * complexity_factor


    allocated_time = max(min_allocation, min(allocated_time, base_time * max_allocation))

    return allocated_time
