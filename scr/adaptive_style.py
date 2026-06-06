import chess
import evaluate
import config


def eval_piece_placement(board: chess.Board, color: chess.Color, phase: str) -> float:
    score = 0.0
    for piece_type in config.PIECE_VALUES.keys():
        for sq in board.pieces(piece_type, color):
            score += evaluate.position_value_get(piece_type, sq, phase, color)
    return score


def measure_opponent(board: chess.Board, opponent_color: chess.Color) -> dict:

    phase = evaluate.game_phase(board)
    flip = opponent_color == chess.BLACK

    ks_raw = evaluate.eval_king_safety(board, opponent_color)
    dp_raw = evaluate.eval_doubled_pawns(board, opponent_color)
    ip_raw = evaluate.eval_isolated_pawns(board, opponent_color)
    rf_raw = evaluate.eval_rook_open_files(board, opponent_color)

    return {
        "king_safety":     -ks_raw  if flip else ks_raw,
        "pawn_strength":   -(dp_raw + ip_raw) if flip else (dp_raw + ip_raw),
        "mobility":        evaluate.eval_mobility(board, opponent_color),
        "rook_activity":   -rf_raw  if flip else rf_raw,
        "piece_placement": eval_piece_placement(board, opponent_color, phase)
    }

def update_profile(board: chess.Board, opponent_color: chess.Color) -> None:
    if not config.adaptive_mode:
        return
    measurements = measure_opponent(board, opponent_color)
    for key, value in measurements.items():
        config.opponent_profile[key] = (
            (1 - config.PROFILE_ALPHA) * config.opponent_profile[key]
            + config.PROFILE_ALPHA * value
        )
    config.profile_move_count += 1

def get_adaptive_bias(board: chess.Board, move: chess.Move, opponent_color: bool) -> float:
    if config.profile_move_count < config.MIN_PROFILE_MOVES:
        return 0.0

    board.push(move)
    after = measure_opponent(board, opponent_color)
    board.pop()

    bias = 0.0
    for key in config.opponent_profile:
        delta = config.opponent_profile[key] - after[key]
        p = config.opponent_profile[key]
        n = config.PROFILE_NORMALIZERS[key]
        if p > 0:
            weakness_factor = max(1.0, n/p)
        elif p < 0:
            weakness_factor = max(1.0, 1.0 - p/n)
        else:
            weakness_factor = 1.0
        bias += delta * weakness_factor * config.PROFILE_WEIGHTS[key]

    return max(-20.0, min(20.0, bias))

def reset_profile() -> None:
    for key in config.opponent_profile:
        config.opponent_profile[key] = 0.0
    config.profile_move_count = 0
