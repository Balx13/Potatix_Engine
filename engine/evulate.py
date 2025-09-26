import chess
from config import position_values, PIECE_VALUES, CENTER_SQUARES
import random # Értékelési zajhoz csak, de az most le van tiltva

def game_phase(board: chess.Board) -> str:
    # egyszerű becslés: anyag alapján
    material = sum(len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK))
                   for pt in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT])
    if material > 12:
        return "opening"
    elif material > 6:
        return "middlegame"
    else:
        return "endgame"


def count_legal_moves(board: chess.Board, color: chess.Color) -> int:
    if board.turn == color:
        return board.legal_moves.count()
    temp_turn = board.turn
    board.turn = color
    count = board.legal_moves.count()
    board.turn = temp_turn
    return count


def evaluate_board(board: chess.Board) -> float:
    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    white_score = 0
    black_score = 0

    # Anyagi érték
    for piece_type, value in PIECE_VALUES.items():
        white_pcs = board.pieces(piece_type, chess.WHITE)
        black_pcs = board.pieces(piece_type, chess.BLACK)
        white_score += len(white_pcs) * value
        black_score += len(black_pcs) * value

        for sq in white_pcs:
            if piece_type == chess.PAWN:
                white_score += position_values["pawn"][sq]
            elif piece_type == chess.BISHOP:
                if game_phase(board) == "endgame":
                    white_score += position_values["bishop_eg"][sq]
                else:
                    white_score += position_values["bishop_eg"][sq]
            elif piece_type == chess.KNIGHT:
                white_score += position_values["knight"][sq]
            elif piece_type == chess.ROOK:
                white_score += position_values["rook"][sq]
            elif piece_type == chess.QUEEN:
                if game_phase(board) == "opening":
                    white_score += position_values["queen_op"][sq]
                else:
                    white_score += position_values["queen_mg"][sq]
            elif piece_type == chess.KING:
                if game_phase(board) == "endgame":
                    white_score += position_values["king_eg"][sq]
                else:
                    white_score += position_values["king_mg"][sq]

        for sq in black_pcs:
            if piece_type == chess.PAWN:
                black_score += position_values["pawn"][sq]
            elif piece_type == chess.BISHOP:
                if game_phase(board) == "endgame":
                    black_score += position_values["bishop_eg"][sq]
                else:
                    black_score += position_values["bishop_eg"][sq]
            elif piece_type == chess.KNIGHT:
                black_score += position_values["knight"][sq]
            elif piece_type == chess.ROOK:
                black_score += position_values["rook"][sq]
            elif piece_type == chess.QUEEN:
                if game_phase(board) == "opening":
                    black_score += position_values["queen_op"][sq]
                else:
                    black_score += position_values["queen_mg"][sq]
            elif piece_type == chess.KING:
                if game_phase(board) == "endgame":
                    black_score += position_values["king_eg"][sq]
                else:
                    black_score += position_values["king_mg"][sq]

    # Központ kontroll
    for sq in CENTER_SQUARES:
        piece = board.piece_at(sq)
        if piece:
            if piece.color == chess.WHITE:
                white_score += 10
            else:
                black_score += 10

    # Mobilitás
    white_score += count_legal_moves(board, chess.WHITE) * 2
    black_score += count_legal_moves(board, chess.BLACK) * 2

    # Királybiztonság
    white_king_sq = board.king(chess.WHITE)
    if white_king_sq is not None:
        white_king_attackers = board.attackers(chess.BLACK, white_king_sq)
        white_score -= len(white_king_attackers) * 20

    black_king_sq = board.king(chess.BLACK)
    if black_king_sq is not None:
        black_king_attackers = board.attackers(chess.WHITE, black_king_sq)
        black_score -= len(black_king_attackers) * 20

    # Izolált gyalogok
    white_score -= count_isolated_pawns(board, chess.WHITE) * 25
    black_score -= count_isolated_pawns(board, chess.BLACK) * 25

    # Dupla gyalogok büntetése
    white_score -= count_doubled_pawns(board, chess.WHITE) * 10
    black_score -= count_doubled_pawns(board, chess.BLACK) * 10

    # futópárok

    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        white_score += 25

    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        black_score += 25


    return (white_score - black_score) / 100.0


def count_doubled_pawns(board, color) -> int:
    pawns = board.pieces(chess.PAWN, color)
    files_count = [0]*8
    for sq in pawns:
        files_count[chess.square_file(sq)] += 1  # minden fájlban megszámoljuk a gyalogokat
    return sum(c-1 for c in files_count if c>1)


def count_isolated_pawns(board, color) -> int:
    pawns = board.pieces(chess.PAWN, color)
    files = [chess.square_file(sq) for sq in pawns]  # fájlok listája
    isolated = 0
    for f in files:
        # Ha nincs gyalog a közvetlen szomszédos fájlokon → izolált
        if (f-1 not in files) and (f+1 not in files):
            isolated += 1
    return isolated

