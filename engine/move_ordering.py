"""
This file is part of Potatix Engine
Copyright (C) 2025-2026 Balázs André
Potatix Engine is licensed under a CUSTOM REDISTRIBUTION LICENSE (see LICENCE.txt)
"""

import chess
from config import killer_moves, PIECE_VALUES, history_heuristic



def sorted_moves_with_value(moves, board):
    # Olyan, mit a sorted() függvény, de azt is visszaadja, hogy az adott lépés hanyas értékkel került az adott helyre

    sortedMoves = []
    for move in moves:
        moves_score = score(move, board)

        inserted = False
        for i in range(len(sortedMoves)):
            if moves_score > sortedMoves[i][1]:
                sortedMoves.insert(i, (move, moves_score))
                inserted = True
                break

        if not inserted:
            sortedMoves.append((move, moves_score))

    return sortedMoves


def history_score(piece, move_):
    # Megmondja egy adott lépésnek a history table score-ját

    if piece:
        piece_type = piece.piece_type
        piece_type -= 1
        history_score_ = history_heuristic[piece_type][move_.from_square][move_.to_square]
    else:
        history_score_ = 0
    return history_score_

def score(move_, board):
    # pontozza az adott lépést egy 0-1250 skálán (az 1250 csak az elméleti maximum)

    piece = board.piece_at(move_.from_square)
    history_score_ = history_score(piece, move_)
    if board.is_capture(move_): # Ütés
        victim = board.piece_at(move_.to_square)
        attacker = board.piece_at(move_.from_square)
        victim_value = PIECE_VALUES[victim.piece_type] if victim else 0
        attacker_value = PIECE_VALUES[attacker.piece_type] if attacker else 0
        return 10 * (victim_value - attacker_value) + 350 + history_score_ # 350-
    board.push(move_)
    if board.is_check(): # Sakk
        board.pop()
        return 150 + history_score_  # 150-250
    board.pop()

    return 5 + history_score_ # 5-105

def order_moves(board, moves, depth):
    # Visszaadja a sorbarendezett lépéseket

    legal_moves_list = list(moves)

    killer_moves_ordered = []

    for move in moves: # Hogyha van egy lépéses matt, akkor azt adjuk csak vissza
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return [(move, 9999)]
        board.pop()

    if depth and killer_moves[depth]:
        for move in killer_moves[depth]:
            if move in legal_moves_list:
                piece = board.piece_at(move.from_square)
                history_score_ = history_score(piece, move)
                killer_moves_ordered.append((move, 1500+history_score_))

    remaining_moves = [m for m in moves if m not in killer_moves_ordered]

    return killer_moves_ordered + sorted_moves_with_value(remaining_moves, board)
