import chess
from config import position_values, PIECE_VALUES, CENTER_SQUARES
import random # Értékelési zajhoz csak, de az most le van tiltva
import adaptive_style

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


def evaluate_board(board: chess.Board, with_muster=False, adaptive_mode=True, engine_white=True, opponent_sytle="balanced"):
    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    white_score = 0
    black_score = 0

    white_material = 0
    black_material = 0
    white_material_list = []
    black_material_list = []
    for piece_type, value in PIECE_VALUES.items():
        # Anyagi érték
        white_pcs = board.pieces(piece_type, chess.WHITE)
        black_pcs = board.pieces(piece_type, chess.BLACK)
        white_material = len(white_pcs) * value
        black_material= len(black_pcs) * value
        white_material_list.append(white_material)
        black_material_list.append(black_material)

        # Pozíciós érték
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
    white_center_control = 0
    black_center_control = 0
    for sq in CENTER_SQUARES:
        piece = board.piece_at(sq)
        if piece:
            if piece.color == chess.WHITE:
                white_center_control += 10
            else:
                black_center_control += 10

    # Mobilitás
    white_mobility = count_legal_moves(board, chess.WHITE) * 2
    black_mobility = count_legal_moves(board, chess.BLACK) * 2

    # Királybiztonság
    white_king_safety = 0
    white_king_sq = board.king(chess.WHITE)
    if white_king_sq is not None:
        white_king_attackers = board.attackers(chess.BLACK, white_king_sq)
        white_king_safety = len(white_king_attackers) * 20

    black_king_safety = 0
    black_king_sq = board.king(chess.BLACK)
    if black_king_sq is not None:
        black_king_attackers = board.attackers(chess.WHITE, black_king_sq)
        black_king_safety = len(black_king_attackers) * 20

    # Izolált gyalogok
    white_isolated_pawns = count_isolated_pawns(board, chess.WHITE) * 25
    black_isolated_pawns = count_isolated_pawns(board, chess.BLACK) * 25

    # Dupla gyalogok büntetése
    white_doubled_pawns = count_doubled_pawns(board, chess.WHITE) * 10
    black_doubled_pawns = count_doubled_pawns(board, chess.BLACK) * 10

    # futópárok

    white_bishops_pair = len(board.pieces(chess.BISHOP, chess.WHITE))
    black_bishops_pair = len(board.pieces(chess.BISHOP, chess.BLACK))

    # gyalogláncok
    white_pawn_chains = count_pawn_chains(board, chess.WHITE)
    black_pawn_chains = count_pawn_chains(board, chess.BLACK)

    # Nyitott vonal a bástyáknak
    white_rook_open_files_count, white_rook_open_files = count_open_files(board, chess.WHITE)
    black_rook_open_files_count, black_rook_open_files  = count_open_files(board, chess.BLACK)

    # Gyenge mezők
    white_weak_squares = count_weak_squares(board, chess.WHITE)
    black_weak_squares = count_weak_squares(board, chess.BLACK)

    # Király támadói
    white_attacks_on_king = count_attacks_on_king(board, chess.WHITE)
    black_attacks_on_king = count_attacks_on_king(board, chess.BLACK)

    # Szabad gyalogok
    white_passed_pawns = count_passed_pawns(board, chess.WHITE)
    black_passed_pawns = count_passed_pawns(board, chess.BLACK)

    musters = {
        "white": {
            "material": white_material,
            "king_safety": white_king_safety,
            "mobility": white_mobility,
            "center_control": white_center_control,
            "pawn_chains": white_pawn_chains,
            "rook_open_files_count": white_rook_open_files_count,
            "rook_open_files": white_rook_open_files,
            "attacks_on_king": white_attacks_on_king,
            "passed_pawns": white_passed_pawns,
            "weak_squares": white_weak_squares
        },
        "black": {
            "material": black_material,
            "king_safety": black_king_safety,
            "mobility": black_mobility,
            "center_control": black_center_control,
            "pawn_chains": black_pawn_chains,
            "rook_open_files_count": black_rook_open_files_count,
            "rook_open_files": black_rook_open_files,
            "attacks_on_king": black_attacks_on_king,
            "passed_pawns": black_passed_pawns,
            "weak_squares": black_weak_squares
        },
        "game_phase": game_phase(board),
        #"evulate": None,
        #"adaptive_evaluation_offset": 1.0,
    }
    white_sytle = "balanced"
    black_sytle = "balanced"

    if adaptive_mode:
        if opponent_sytle == adaptive_style.playing_style_recognition(musters, not engine_white):
            if engine_white:
                black_score *= 1.2
            else:
                white_score *= 1.2
        else:
            if engine_white:
                black_score *= 0.8
            else:
                white_score *= 0.8
        if adaptive_style.counter_styles[opponent_sytle] == adaptive_style.playing_style_recognition(musters, engine_white):
            if engine_white:
                white_score *= 1.2
            else:
                white_score *= 1.2
        else:
            if engine_white:
                white_score *= 0.8
            else:
                white_score *= 0.8

        if engine_white:
            black_sytle = opponent_sytle
            white_sytle = adaptive_style.counter_styles[opponent_sytle]
        else:
            white_sytle = opponent_sytle
            black_sytle = adaptive_style.counter_styles[opponent_sytle]

    # hogyha nincs adaptive_mode, akkor a szorzó mindig 1.0
    white_score += white_center_control * adaptive_style.sytles[white_sytle]["center_control"]
    black_score += black_center_control * adaptive_style.sytles[black_sytle]["center_control"]

    white_score += white_mobility * adaptive_style.sytles[white_sytle]["mobility"]
    black_score += black_mobility * adaptive_style.sytles[black_sytle]["mobility"]

    white_score -= white_king_safety * adaptive_style.sytles[white_sytle]["king_safety"]
    black_score -= black_king_safety * adaptive_style.sytles[black_sytle]["king_safety"]

    white_score -= white_isolated_pawns
    black_score -= black_isolated_pawns

    white_score -= white_doubled_pawns
    black_score -= black_doubled_pawns

    if white_bishops_pair >= 2:
        white_score += 25
    if black_bishops_pair >= 2:
        black_score += 25

    white_score += (white_pawn_chains * 12) * adaptive_style.sytles[white_sytle]["pawn_chains"]
    black_score += (black_pawn_chains * 12) * adaptive_style.sytles[black_sytle]["pawn_chains"]

    white_score += white_rook_open_files_count * 22  * adaptive_style.sytles[white_sytle]["rook_open_files"]
    black_score += black_rook_open_files_count * 22  * adaptive_style.sytles[black_sytle]["rook_open_files"]

    white_score += (white_weak_squares * -7) * adaptive_style.sytles[white_sytle]["weak_squares"]
    black_score += (black_weak_squares * -7) * adaptive_style.sytles[black_sytle]["weak_squares"]

    white_score -= (white_attacks_on_king * 36) * adaptive_style.sytles[white_sytle]["attacks_on_king"]
    black_score -= (black_attacks_on_king * 36) * adaptive_style.sytles[black_sytle]["attacks_on_king"]

    white_score += (white_passed_pawns * 52) * adaptive_style.sytles[white_sytle]["passed_pawns"]
    black_score += (black_passed_pawns * 52) * adaptive_style.sytles[black_sytle]["passed_pawns"]

    for i in white_material_list:
        white_score += i * adaptive_style.sytles[white_sytle]["material"]
    for i in black_material_list:
        black_score += i * adaptive_style.sytles[black_sytle]["material"]

    if with_muster:
        return (white_score - black_score) / 100.0, musters
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

def count_open_files(board, color):
    count = 0
    open_files = []
    for f in range(8):
        # Ha nincs saját gyalog a fájlban
        if not any(chess.square_file(sq) == f and board.piece_at(sq).piece_type == chess.PAWN and board.piece_at(sq).color == color for sq in board.pieces(chess.PAWN, color)):
            # Ha van bástya a fájlban → nyitott vonal
            if (chess.square_file(sq) == f and board.piece_at(sq).piece_type == chess.ROOK and board.piece_at(sq).color == color for sq in board.pieces(chess.ROOK, color)):
                count += 1
                open_files.append(f)
    return count, open_files

def count_weak_squares(board, color) -> int:
    count = 0
    opp_color = not color
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        # Gyenge mező: nincs védve saját figurával, ellenfél támadja
        if piece is None and len(board.attackers(color, sq)) == 0 and len(board.attackers(opp_color, sq)) > 0:
            count += 1
    return count

def count_attacks_on_king(board, color) -> int:
    king_sq = board.king(color)
    if king_sq is None:
        return 0
    return len(board.attackers(not color, king_sq))

def count_pawn_chains(board, color) -> int:
    direction = 1 if color == chess.WHITE else -1
    chains = 0

    for sq in board.pieces(chess.PAWN, color):
        file = chess.square_file(sq)
        rank = chess.square_rank(sq) + direction

        for df in (-1, 1):
            f = file + df
            if 0 <= f <= 7 and 0 <= rank <= 7:
                target = chess.square(f, rank)
                piece = board.piece_at(target)
                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                    chains += 1

    return chains

def count_passed_pawns(board, color) -> int:
    passed = 0
    direction = 1 if color == chess.WHITE else -1
    enemy_pawns = board.pieces(chess.PAWN, not color)

    for sq in board.pieces(chess.PAWN, color):
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)

        blocked = False
        for ep in enemy_pawns:
            ef, er = chess.square_file(ep), chess.square_rank(ep)

            # Ugyanazon vagy szomszédos fájlon, és előtte áll
            if abs(ef - file) <= 1 and (er - rank) * direction > 0:
                blocked = True
                break

        if not blocked:
            passed += 1

    return passed