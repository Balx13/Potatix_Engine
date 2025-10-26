import chess
from config import killer_moves, PIECE_VALUES, history_heuristic
from evulate import evaluate_board
from adaptive_style import playing_style_recognition, counter_styles

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

    def score(move):
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            victim_value = PIECE_VALUES[victim.piece_type] if victim else 0
            attacker_value = PIECE_VALUES[attacker.piece_type] if attacker else 0
            return 10 * (victim_value - attacker_value) + 100

        board.push(move)
        if board.is_check():
            board.pop()
            if followed_style():
                return 50
            else:
                return 10
        board.pop()

        piece = board.piece_at(move.from_square)
        if piece:
            piece_type = piece.piece_type
            from_sq = move.from_square
            to_sq = move.to_square
            history_score = history_heuristic[piece_type][from_sq][to_sq]
        else:
            history_score = 0

        if followed_style():
            return 5 + history_score
        else:
            return 0 + history_score

    remaining_moves = sorted(remaining_moves, key=score, reverse=True)
    return killer_moves_ordered + remaining_moves
