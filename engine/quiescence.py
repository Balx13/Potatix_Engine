import chess
from move_ordering import order_moves
from evulate import evaluate_board
from config import PIECE_VALUES

def see(board, move):
    from_square = move.from_square
    to_square = move.to_square

    attacker = board.piece_at(from_square)
    victim = board.piece_at(to_square)

    # gain lista: minden lépés után mennyit nyerünk/vesztünk
    gain = []
    gain.append(PIECE_VALUES[victim.piece_type] if victim else 0)

    # átmeneti állapot: kik támadják a célmezőt
    occupied = board.occupied
    attackers = board.attackers(chess.WHITE, to_square) | board.attackers(chess.BLACK, to_square)

    # az ütést végrehajtjuk (attacker átmegy a célmezőre)
    occupied ^= chess.BB_SQUARES[from_square]
    occupied ^= chess.BB_SQUARES[to_square]

    color = not attacker.color  # most az ellenfélé jön

    while True:
        # kik tudják visszaütni a célmezőt most?
        attackers &= occupied
        possible = [sq for sq in attackers if board.piece_at(sq).color == color]
        if not possible:
            break

        # a legolcsóbb bábuval üssön vissza az ellenfél
        sq = min(possible, key=lambda s: PIECE_VALUES[board.piece_at(s).piece_type])
        piece = board.piece_at(sq)

        # új gain: előző - az ütő bábu értéke
        gain.append(-gain[-1] + PIECE_VALUES[piece.piece_type])

        # frissítjük az állapotot (ő is átáll a célmezőre)
        occupied ^= chess.BB_SQUARES[sq]
        color = not color

    # optimális pont: a sorozat maximuma
    result = max((-1)**i * g for i, g in enumerate(gain))
    return result



# Quiescence search (csak capture lépéseket vizsgál)
def quiescence(board: chess.Board, maximizing_player: bool, alpha: float, beta: float) -> float:
    stand_pat = evaluate_board(board)

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

    for move in order_moves(board, board.legal_moves):

        if see(board, move) <= 0:
            continue

        if board.is_capture(move):
            board.push(move)
            score = quiescence(board, not maximizing_player, alpha, beta)
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
