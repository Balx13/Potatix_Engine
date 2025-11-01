import chess
from config import killer_moves, PIECE_VALUES, history_heuristic, counter_styles
from evulate import evaluate_board
from adaptive_style import playing_style_recognition

def order_moves(board, moves, depth=None, datas_for_evulate=None):
    if datas_for_evulate is None:
        datas_for_evulate = []
    legal_moves_list = list(moves)

    killer_moves_ordered = []

    if depth and killer_moves[depth]:
        for move in killer_moves[depth]:
            if move in legal_moves_list:
                killer_moves_ordered.append(move)

    remaining_moves = [m for m in moves if m not in killer_moves_ordered]

    def followed_style():
        engine_is_white = datas_for_evulate[1]
        _, musters = evaluate_board(board, with_muster=True)

        opponent_style = datas_for_evulate[0]
        motor_to_move = (engine_is_white == board.turn)
        expected_style = counter_styles[opponent_style] if motor_to_move else opponent_style

        if playing_style_recognition(musters, board.turn) == expected_style:
            return True
        else:
            return False

    def score(move_):
        piece = board.piece_at(move_.from_square)
        followed_s = followed_style()
        if piece:
            piece_type = piece.piece_type
            piece_type -= 1
            history_score = history_heuristic[piece_type][move_.from_square][move_.to_square]
        else:
            history_score = 0

        if board.is_capture(move_): # Ütés
            victim = board.piece_at(move_.to_square)
            attacker = board.piece_at(move_.from_square)
            victim_value = PIECE_VALUES[victim.piece_type] if victim else 0
            attacker_value = PIECE_VALUES[attacker.piece_type] if attacker else 0
            if followed_s:
                return 10 * (victim_value - attacker_value) + 350 + history_score # 350-
            else:
                return 10 * (victim_value - attacker_value) + 300 + history_score  # 300-

        board.push(move_)
        if board.is_check(): # Sakk
            board.pop()
            if followed_s:
                return 150 + history_score # 150-250
            else:
                return 100  + history_score# 100-200
        board.pop()

        if followed_s: # Maradék
            return 5 + history_score # 5-105
        else:
            return 0 + history_score # 0-100

    remaining_moves = sorted(remaining_moves, key=score, reverse=True)
    return killer_moves_ordered + remaining_moves
