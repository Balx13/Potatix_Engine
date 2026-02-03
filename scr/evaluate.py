"""
This file is part of Potatix Engine
Copyright (C) 2025-2026 Balázs André

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import chess
import config
import math

def truncate(x: float) -> float:
    factor = 10**4  # 4 tizedesjegy megtartása
    return math.trunc(x * factor) / factor


def game_phase(board: chess.Board) -> str:
    # Azt próbálja megmondani, hogy megnyitásban, középjátékban, vagy végjátékban vagyunk

    material = sum(len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK))
                   for pt in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT])

    white_king_rank = chess.square_rank(board.king(chess.WHITE))
    black_king_rank = chess.square_rank(board.king(chess.BLACK))
    king_distance_from_starting = max(white_king_rank, abs(black_king_rank-7))  # Melyik soron van a király

    if material > 12 and king_distance_from_starting <= 1:
        return "opening"
    elif material < 6 or king_distance_from_starting > 2:
        return "endgame"
    return "middlegame"


def position_value_get(piece_type, sq_, phase) -> float:
    sq = chess.square_mirror(sq_)
    if piece_type == chess.PAWN:
        return config.position_values["pawn"][sq]
    elif piece_type == chess.KNIGHT:
        return config.position_values["knight"][sq]
    elif piece_type == chess.BISHOP:
        if phase == "endgame":
            return config.position_values["bishop_eg"][sq]
        else:
            return config.position_values["bishop_mg"][sq]
    elif piece_type == chess.ROOK:
        return config.position_values["rook"][sq]
    elif piece_type == chess.QUEEN:
        if phase == "opening":
            return config.position_values["queen_op"][sq]
        else:
            return config.position_values["queen_mg"][sq]
    elif piece_type == chess.KING:
        if phase == "endgame":
            return config.position_values["king_eg"][sq]
        else:
            return config.position_values["king_mg"][sq]
    return 0


def eval_position_values(board: chess.Board, phase) -> float:
    score = 0
    for piece_type in config.PIECE_VALUES.keys():
        for sq in board.pieces(piece_type, chess.WHITE):
            score += position_value_get(piece_type, sq, phase)
        for sq in board.pieces(piece_type, chess.BLACK):
            score -= position_value_get(piece_type, chess.square_mirror(sq), phase)
    return score


def eval_material(board: chess.Board, color_param=None) -> float:
    # A color_param paraméter akkor használatos, hogyha csak az egyik felet akarjuk mérni
    score = 0
    for piece, value in config.PIECE_VALUES.items():
        if color_param is not None:
            score += len(board.pieces(piece, color_param)) * value
        else:
            score += len(board.pieces(piece, chess.WHITE)) * value
            score -= len(board.pieces(piece, chess.BLACK)) * value
    return score

def eval_mobility(board: chess.Board, color_param=None) -> float:
    # A color_param paraméter akkor használatos, hogyha csak az egyik felet akarjuk mérni
    def mobility(colorr):
        old_turn = board.turn
        board.turn = colorr
        data = board.legal_moves.count()
        board.turn = old_turn
        return data
    if color_param is not None:
        mobility_score = mobility(color_param)
    else:
        mobility_score = (mobility(chess.WHITE) - mobility(chess.BLACK))
    return mobility_score * 1.1

def eval_king_safety(board: chess.Board, color_param=None) -> float:
    # A color_param paraméter akkor használatos, hogyha csak az egyik felet akarjuk mérni
    score = 0

    ATTACK_WEIGHTS = {
        chess.PAWN: 1,
        chess.KNIGHT: 2,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 4
    }
    if color_param is not None:
        colors = (color_param,)
    else:
        colors = (chess.WHITE, chess.BLACK)
    for color in colors:
        king_sq = board.king(color)
        if king_sq is None:
            continue
        sign = 1 if color == chess.WHITE else -1
        zone = chess.SquareSet(chess.BB_KING_ATTACKS[king_sq])
        danger = 0

        # Ellenséges támadások
        for piece_type, weight in ATTACK_WEIGHTS.items():
            for sq in board.pieces(piece_type, not color):
                attacks = board.attacks(sq)
                danger += weight * len(attacks & zone)

        # Gyalogpajzs
        file = chess.square_file(king_sq)
        rank = chess.square_rank(king_sq)
        shield_rank = rank + 1 if color == chess.WHITE else rank - 1
        is_castled_side = file <= 2 or file >= 5
        if 0 <= shield_rank <= 7:
            for df in (-1, 0, 1):
                f = file+df
                if 0 <= f <= 7:
                    shield_sq = chess.square(f, shield_rank)
                    if board.piece_at(shield_sq) != chess.Piece(chess.PAWN, color):
                        fianchetto_rank = shield_rank + (1 if color == chess.WHITE else -1)
                        if 0 <= fianchetto_rank <= 7:
                            fianchetto_sq = chess.square(f, fianchetto_rank)
                            if board.piece_at(fianchetto_sq) == chess.Piece(chess.PAWN, color):
                                if is_castled_side:
                                    danger += 0.5
                                else:
                                    danger += 0.25
                            else:
                                if is_castled_side:
                                    danger += 2
                                else:
                                    danger += 1

        score -= sign * danger * 10
    return score

def eval_doubled_pawns(board: chess.Board, color_param=None) -> float:
    # A color_param paraméter akkor használatos, hogyha csak az egyik felet akarjuk mérni
    score = 0
    if color_param is not None:
        colors = (color_param,)
    else:
        colors = (chess.WHITE, chess.BLACK)
    for color in colors:
        pawns = board.pieces(chess.PAWN, color)
        sign = -1 if color == chess.WHITE else 1
        files_count = [0]*8
        for sq in pawns:
            files_count[chess.square_file(sq)] += 1
        double_pawns = sum(c-1 for c in files_count if c>1)
        score += sign * 10 * double_pawns
    return score


def eval_isolated_pawns(board: chess.Board, color_param=None) -> float:
    # A color_param paraméter akkor használatos, hogyha csak az egyik felet akarjuk mérni
    score = 0
    if color_param is not None:
        colors = (color_param,)
    else:
        colors = (chess.WHITE, chess.BLACK)
    for color in colors:
        pawns = board.pieces(chess.PAWN, color)
        files = [chess.square_file(sq) for sq in pawns]
        sign = -1 if color == chess.WHITE else 1
        isolated = 0
        for f in files:
            if (f-1 not in files) and (f+1 not in files):
                isolated += 1
        score += sign * isolated * 25
    return score


def eval_passed_pawns(board: chess.Board) -> float:
    score = 0
    PASSED_PAWN_BONUS = [0, 0, 10, 20, 35, 60, 90, 0]

    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)

    for sq in white_pawns:
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)
        is_passed = True
        for ep in black_pawns:
            ep_file = chess.square_file(ep)
            ep_rank = chess.square_rank(ep)
            if abs(ep_file-file) <= 1 and ep_rank > rank:
                is_passed = False
                break
        if is_passed:
            score += PASSED_PAWN_BONUS[rank]

    for sq in black_pawns:
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)
        is_passed = True
        for ep in white_pawns:
            ep_file = chess.square_file(ep)
            ep_rank = chess.square_rank(ep)
            if abs(ep_file-file) <= 1 and ep_rank < rank:
                is_passed = False
                break
        if is_passed:
            score -= PASSED_PAWN_BONUS[7-rank]
    return score


def eval_pawns(board: chess.Board) -> float:
    score = 0

    score += eval_doubled_pawns(board)
    score += eval_isolated_pawns(board)
    score += eval_passed_pawns(board)

    return score

def eval_rook_open_files(board: chess.Board, color_param=None) -> float:
    # A color_param paraméter akkor használatos, hogyha csak az egyik felet akarjuk mérni
    score = 0
    if color_param is not None:
        colors = (color_param,)
    else:
        colors = (chess.WHITE, chess.BLACK)

    for color in colors:
        sign = 1 if color == chess.WHITE else -1
        pawns = board.pieces(chess.PAWN, color)
        opp_pawns = board.pieces(chess.PAWN, not color)
        pawn_files = {chess.square_file(sq) for sq in pawns}
        opp_pawn_files = {chess.square_file(sq) for sq in opp_pawns}

        for rook_sq in board.pieces(chess.ROOK, color):
            f = chess.square_file(rook_sq)
            if f not in pawn_files and f not in opp_pawn_files:
                score += sign * 20
            elif f not in pawn_files:
                score += sign * 10
    return score

def eval_bishop_pair(board) -> float:
    score = 0
    base = 25
    OPEN_BONUS = 10

    total_pawns = len(board.pieces(chess.PAWN, chess.WHITE)) + \
                  len(board.pieces(chess.PAWN, chess.BLACK))

    open_factor = OPEN_BONUS if total_pawns <= 10 else 0


    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += base + open_factor
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= base + open_factor
    return score

def evaluate(board: chess.Board, ply) -> float:
    ######################
    # Objektív értékelés #
    ######################

    mate_score = 1_000_000
    if board.is_checkmate():
        return -mate_score+ply if board.turn else mate_score-ply
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    phase = game_phase(board)
    w = config.tapered_weights[phase]
    score = 0.0
    position_values_score = eval_position_values(board, phase)
    bishop_pair_score = eval_bishop_pair(board) * w["bishop_pair"]
    material_score = eval_material(board)
    mobility_score = eval_mobility(board) * w["mobility"]
    king_safety_score = eval_king_safety(board) * w["king_safety"]
    pawns_score = eval_pawns(board) * w["pawn_structure"]
    rook_open_files_score = eval_rook_open_files(board) * w["rook_files"]

    #############
    # Összeadás #
    #############
    score += position_values_score
    score += bishop_pair_score
    score += material_score
    score += mobility_score
    score += king_safety_score
    score += pawns_score
    score += rook_open_files_score
    score = truncate(score)
    if score == -0.0:
        return 0.0
    return score

def test_startpos():
    assert abs(evaluate(chess.Board())) < 5

def test_symmetry(fen):
    b = chess.Board(fen)
    s1 = evaluate(b)
    b.apply_mirror()
    s2 = evaluate(b)
    print(f"DEBUG: s1: {s1}, s2: {s2}")
    assert abs(s1 + s2) < 5

#test_startpos()
#print(evaluate(chess.Board("r1b2r1k/1pp3pp/2n5/p1Q1p1q1/8/2NP2P1/PP2PPBP/R4RK1 b - - 0 13")))

#test_symmetry("r1b2r1k/1pp3pp/2n5/p1Q1p1q1/8/2NP2P1/PP2PPBP/R4RK1 b - - 0 13")
#test_symmetry("rnbqkbnr/pppppppp/8/8/8/1P6/P1PPPPPP/RNBQKBNR b KQkq - 0 1")