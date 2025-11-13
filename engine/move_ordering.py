"""
This file is part of Potatix Engine
Copyright (C) 2025 Balázs André
Potatix Engine is licensed under a CUSTOM REDISTRIBUTION LICENSE (see LICENCE.txt)
"""

import chess
from config import killer_moves, PIECE_VALUES, history_heuristic, counter_styles
from evulate import evaluate_board
from adaptive_style import playing_style_recognition


def sorted_moves_with_value(moves, board, datas_for_evulate):
    # Olyan, mit a sorted() függvény, de azt is visszaadja, hogy az adott lépés hanyas értékkel került az adott helyre

    sortedMoves = []
    for move in moves:
        moves_score = score(move, board, datas_for_evulate)

        inserted = False
        for i in range(len(sortedMoves)):
            if moves_score > sortedMoves[i][1]:
                sortedMoves.insert(i, (move, moves_score))
                inserted = True
                break

        if not inserted:
            sortedMoves.append((move, moves_score))

    return sortedMoves


def followed_style(board, datas_for_evulate):
    # Visszaadja a soron következő játékos stílusát

    engine_is_white = datas_for_evulate[1]
    _, musters = evaluate_board(board, with_muster=True)

    opponent_style = datas_for_evulate[0]
    engine_to_move = (engine_is_white == board.turn)
    expected_style = counter_styles[opponent_style] if engine_to_move else opponent_style

    if playing_style_recognition(musters, board.turn) == expected_style:
        return True
    else:
        return False

def history_score(piece, move_):
    # Megmondja egy adott lépésnek a history table score-ját

    if piece:
        piece_type = piece.piece_type
        piece_type -= 1
        history_score_ = history_heuristic[piece_type][move_.from_square][move_.to_square]
    else:
        history_score_ = 0
    return history_score_

def score(move_, board, datas_for_evulate):
    # pontozza az adott lépést egy 0-1250 skálán (az 1250 csak az elméleti maximum)

    piece = board.piece_at(move_.from_square)
    followed_s = followed_style(board, datas_for_evulate)
    history_score_ = history_score(piece, move_)
    if board.is_capture(move_): # Ütés
        victim = board.piece_at(move_.to_square)
        attacker = board.piece_at(move_.from_square)
        victim_value = PIECE_VALUES[victim.piece_type] if victim else 0
        attacker_value = PIECE_VALUES[attacker.piece_type] if attacker else 0
        if followed_s:
            return 10 * (victim_value - attacker_value) + 350 + history_score_ # 350-
        else:
            return 10 * (victim_value - attacker_value) + 300 + history_score_  # 300-

    board.push(move_)
    if board.is_check(): # Sakk
        board.pop()
        if followed_s:
            return 150 + history_score_  # 150-250
        else:
            return 100  + history_score_ # 100-200
    board.pop()

    if followed_s: # Maradék
        return 5 + history_score_ # 5-105
    else:
        return 0 + history_score_ # 0-100

def order_moves(board, moves, depth, datas_for_evulate):
    # Visszaadja a sorbarendezett lépéseket

    if datas_for_evulate is None:
        datas_for_evulate = []
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

    return killer_moves_ordered + sorted_moves_with_value(remaining_moves, board, datas_for_evulate)
