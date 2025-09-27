import chess
from config import PIECE_VALUES
def estimate_time_for_move(board: chess.Board, base_time: float, increment: float, moves_to_go=None) -> float:

    move_number = board.fullmove_number
    if move_number < 15:
        phase_factor = 0.6
    elif move_number < 40:
        phase_factor = 1.0
    else:
        phase_factor = 1.3

    material_balance = 0

    for piece_type, value in PIECE_VALUES.items():
        material_balance += len(board.pieces(piece_type, chess.WHITE)) * value
        material_balance -= len(board.pieces(piece_type, chess.BLACK)) * value

    if abs(material_balance) <= 200:
        complexity_factor = 1.2  # kiegyenlítettebb állás → több gondolkodás
    else:
        complexity_factor = 0.8  # nagyobb előny egyik félnél → kevesebb idő is elég

    # 3. Időelosztás (átlagos lépésszámra osztva)
    if not moves_to_go:
        moves_to_go = 40
    base_allocation = (base_time / moves_to_go) + increment

    # 4. Végső idő számítás
    allocated_time = base_allocation * phase_factor * complexity_factor

    # 5. Minimum és maximum korlát
    allocated_time = max(0.05, min(allocated_time, base_time * 0.5))

    return allocated_time
