import chess
from config import PIECE_VALUES

def estimate_moves_to_go(board: chess.Board) -> int:

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

    return estimated_moves_to_go


def estimate_time_for_move(board: chess.Board, base_time: float, increment: float, moves_to_go=None) -> float:

    move_number = board.fullmove_number
    if move_number < 15:
        phase_factor = 0.9
    elif move_number < 40:
        phase_factor = 1.0
    else:
        phase_factor = 1.2

    material_balance = 0

    for piece_type, value in PIECE_VALUES.items():
        material_balance += len(board.pieces(piece_type, chess.WHITE)) * value
        material_balance -= len(board.pieces(piece_type, chess.BLACK)) * value

    if abs(material_balance) <= 200:
        complexity_factor = 1.2
    else:
        complexity_factor = 0.9

    if not moves_to_go:
        moves_to_go = estimate_moves_to_go(board)
    base_allocation = (base_time / moves_to_go) + increment

    allocated_time = base_allocation * phase_factor * complexity_factor

    allocated_time = max(0.05, min(allocated_time, base_time * 0.5))

    return allocated_time
