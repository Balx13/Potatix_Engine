"""
This file is part of Potatix Engine
Copyright (C) 2025-2026 Balázs André
Potatix Engine is licensed under a CUSTOM REDISTRIBUTION LICENSE (see LICENCE.txt)
"""

import chess
import config


def sorted_moves_with_value(moves, board) ->list:
    # Olyan, mit a sorted() függvény, de azt is visszaadja, hogy az adott lépés hányas értékkel került az adott helyre

    sorted_moves = []
    for move in moves:
        moves_score = score(move, board)

        inserted = False
        for i in range(len(sorted_moves)):
            if moves_score > sorted_moves[i][1]:
                sorted_moves.insert(i, (move, moves_score))
                inserted = True
                break

        if not inserted:
            sorted_moves.append((move, moves_score))

    return sorted_moves


def history_score(board, move_):
    # Megmondja egy adott lépésnek a history table score-ját
    piece = board.piece_at(move_.from_square)

    if piece:
        piece_type = piece.piece_type
        piece_type -= 1
        history_score_ = config.history_heuristic[piece_type][move_.from_square][move_.to_square]
    else:
        history_score_ = 0
    return history_score_

def score(move_, board):
    # pontozza az adott lépést
    m = config.multipliers["engine"] if config.engine_turn else config.multipliers["oppoment"]
    piece = board.piece_at(move_.from_square)
    pt = piece.piece_type if piece else None
    history_score_ = history_score(board, move_)
    if board.is_capture(move_): # Ütés
        victim = board.piece_at(move_.to_square)
        attacker = piece # piece = board.piece_at(move_.from_square)
        victim_value = config.PIECE_VALUES[victim.piece_type] if victim else 0
        attacker_value = config.PIECE_VALUES[attacker.piece_type] if attacker else 0
        return 1000 + 10 * victim_value - attacker_value + history_score_

    board.push(move_)
    is_check = board.is_check()
    board.pop()
    if is_check:
        check_bonus = 100 * m.get("king_safety", 1.0)
        return 500 + check_bonus + history_score_

    quiet_score = 10 + history_score_
    if pt == chess.BISHOP:
        quiet_score += m.get("bishop_pairs", 1.0) * 100
    elif pt == chess.ROOK:
        quiet_score += m.get("rook_op_files", 1.0) * 100

    quiet_score += m.get("mobility", 1.0) * 50
    quiet_score += 100

    return quiet_score

def order_moves(board, moves, depth) -> list:
    """

    :param board: chess.Board
    :param moves: chess.Move
    :param depth: int
    :return: list of moves

    Move ordering

    Move weights:
    - Killer moves: 10000-10100
    - Capture moves: 1000-9100
    - Check moves: 570-730
    - Quiet moves: 145-405

    """
    # Visszaadja a sorbarendezett lépéseket

    legal_moves_list = list(moves)

    killer_moves_ordered = []

    for move in moves: # Hogyha van egy lépéses matt, akkor azt adjuk csak vissza
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return [(move, 9999999)]
        board.pop()
    if depth < len(config.killer_moves):
        if depth and config.killer_moves[depth]:
            for move in config.killer_moves[depth]:
                if move in legal_moves_list:
                    killer_moves_ordered.append((move, 10_000+history_score(board, move)))
    if len(killer_moves_ordered) >= 2: # Ha van legalább két lépés, akkor rangsoroljuk
        km = sorted_moves_with_value(killer_moves_ordered, board)
        killer_moves_ordered = [(move_, 10_000+history_score(board, move_)) for move_, _ in km]

    remaining_moves = [m for m in moves if m not in killer_moves_ordered]

    return killer_moves_ordered + sorted_moves_with_value(remaining_moves, board)
