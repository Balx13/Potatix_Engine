import chess
from config import killer_moves, PIECE_VALUES

def order_moves(board, moves, depth=None):
    legal_moves_list = list(moves)

    killer_moves_ordered = []

    if depth and killer_moves[depth]:
        for move in killer_moves[depth]:
            if move in legal_moves_list:
                killer_moves_ordered.append(move)

    remaining_moves = [m for m in moves if m not in killer_moves_ordered]

    def score(move):
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            victim_value = PIECE_VALUES[victim.piece_type] if victim else 0
            attacker_value = PIECE_VALUES[attacker.piece_type] if attacker else 0
            return 10 * (victim_value - attacker_value) + 100

        board.push(move)
        check = 1 if board.is_check() else 0
        board.pop()
        return check

    remaining_moves = sorted(remaining_moves, key=score, reverse=True)
    return killer_moves_ordered + remaining_moves
