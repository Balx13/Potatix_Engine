import chess
from move_ordering import order_moves
from evulate import evaluate_board
from config import PIECE_VALUES

def see(board, move):
    from_square = move.from_square
    to_square = move.to_square

    attacker = board.piece_at(from_square)
    victim = board.piece_at(to_square)

    gain = [PIECE_VALUES[victim.piece_type] if victim else 0]

    occupied = board.occupied
    attackers = board.attackers(chess.WHITE, to_square) | board.attackers(chess.BLACK, to_square)

    occupied ^= chess.BB_SQUARES[from_square]
    occupied ^= chess.BB_SQUARES[to_square]

    color = not attacker.color

    while True:

        attackers &= occupied
        possible = [sq for sq in attackers if board.piece_at(sq).color == color]
        if not possible:
            break

        sq = min(possible, key=lambda s: PIECE_VALUES[board.piece_at(s).piece_type])
        piece = board.piece_at(sq)

        gain.append(-gain[-1] + PIECE_VALUES[piece.piece_type])

        occupied ^= chess.BB_SQUARES[sq]
        color = not color

    result = max((-1)**i * g for i, g in enumerate(gain))
    return result


def quiescence(board: chess.Board, maximizing_player: bool, alpha: float, beta: float, datas_for_evulate) -> float:
    stand_pat = evaluate_board(board, with_muster=False, adaptive_mode=datas_for_evulate[2],
        engine_white=datas_for_evulate[1], opponent_sytle=datas_for_evulate[0])

    if maximizing_player:
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
    else:
        if stand_pat <= alpha:
            return alpha
        if stand_pat < beta:
            beta = stand_pat

    for move in order_moves(board, board.legal_moves, datas_for_evulate=datas_for_evulate):

        if see(board, move) <= 0:
            continue

        if board.is_capture(move):
            board.push(move)
            score = quiescence(board, not maximizing_player, alpha, beta, datas_for_evulate)
            board.pop()

            if maximizing_player:
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
            else:
                if score <= alpha:
                    return alpha
                if score < beta:
                    beta = score

    return alpha if maximizing_player else beta
