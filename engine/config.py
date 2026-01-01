"""
This file is part of Potatix Engine
Copyright (C) 2025-2026 Balázs André
Potatix Engine is licensed under a CUSTOM REDISTRIBUTION LICENSE (see LICENCE.txt)
"""


# Ebben a fájlban vannak az adatok/mátrixok/változók nagyrésze

import chess

# Kezdőállás
board = chess.Board(chess.STARTING_FEN)

MAX_DEPTH = 100_000

killer_moves = [[] for _ in range(MAX_DEPTH)]

history_heuristic = [[[0 for _ in range(64)] for _ in range(64)] for _ in range(6)]

PIECE_VALUES = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:   0
}

CENTER_SQUARES = [chess.D4, chess.D5, chess.E4, chess.E5]


position_values = {
    "pawn": (
         0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
         5,  5, 10, 25, 25, 10,  5,  5,
         0,  0,  0, 20, 20,  0,  0,  0,
         5, -5,-10,  0,  0,-10, -5,  5,
         5, 10, 10,-20,-20, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0
    ),

    "bishop_mg": (
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10, -3,  5, 10, 10,  5, -3,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ),

    "bishop_eg": (
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ),

    "knight": (
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ),

    "rook": (
         0,  0,  0,  0,  0,  0,  0, 0,
         5, 10, 10, 10, 10, 10, 10, 5,
        -5,  0,  0,  0,  0,  0,  0,-5,
        -5,  0,  0,  0,  0,  0,  0,-5,
        -5,  0,  0,  0,  0,  0,  0,-5,
        -5,  0,  0,  0,  0,  0,  0,-5,
        -5,  0,  0,  0,  0,  0,  0,-5,
         0,  0,  0,  5,  5,  0,  0, 0
    ),

    "queen_mg": (
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,   0,  5,  5,  5,  5,  0, -5,
         0,   0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ),

    "queen_op": (
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10, -5, -5, -5, -5, -5, -5,-10,
        -10, -1, -5, -5, -5, -5, -1,-10,
        -5,  -1, -3, -5, -5, -3, -1, -5,
         0,  -1, -3, -5, -5, -3, -1, -5,
        -10, -1,  0,  0,  0, -3, -1,-10,
        -10,  0,  0,  5,  5,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ),

    "king_mg": (
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20, 20,  0,  0,  0,  0, 20, 20,
         20, 30, 10,  0,  0, 10, 30, 20
    ),

    "king_eg": (
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50
    )
}

tapered_weights = {
    "opening": {
        "king_safety": 1.2,
        "mobility": 0.8,
        "pawn_structure": 1.0,
        "rook_files": 0.8,
        "bishop_pair": 0.9
    },
    "middlegame": {
        "king_safety": 1.0,
        "mobility": 1.0,
        "pawn_structure": 1.0,
        "rook_files": 1.0,
        "bishop_pair": 1.0
    },
    "endgame": {
        "king_safety": 0.5,
        "mobility": 1.2,
        "pawn_structure": 1.1,
        "rook_files": 1.2,
        "bishop_pair": 1.1
    }
}

styles = {
    "attacker": {
        "material":        0.85,
        "king_safety":     0.7,
        "mobility":        1.4,
        "center_control":  1.1,
        "pawn_chains":     0.9,
        "rook_open_files": 1.3,
        "attacks_on_king": 1.6,
        "passed_pawns":    0.8,
        "weak_squares":    0.7
    },
    "defensive": {
        "material":        1.2,
        "king_safety":     1.6,
        "mobility":        0.8,
        "center_control":  1.3,
        "pawn_chains":     1.4,
        "rook_open_files": 0.6,
        "attacks_on_king": 0.4,
        "passed_pawns":    1.0,
        "weak_squares":    0.9
    },
    "positional": {
        "material":        1.0,
        "king_safety":     1.2,
        "mobility":        1.0,
        "center_control":  1.5,
        "pawn_chains":     1.3,
        "rook_open_files": 0.9,
        "attacks_on_king": 0.7,
        "passed_pawns":    1.0,
        "weak_squares":    0.6
    },
    "tactical": {
        "material":        0.9,
        "king_safety":     0.8,
        "mobility":        1.5,
        "center_control":  1.0,
        "pawn_chains":     0.8,
        "rook_open_files": 1.4,
        "attacks_on_king": 1.5,
        "passed_pawns":    0.9,
        "weak_squares":    0.8
    },
    "endgame": {
        "material":        1.0,
        "king_safety":     1.0,
        "mobility":        0.8,
        "center_control":  1.1,
        "pawn_chains":     1.3,
        "rook_open_files": 0.8,
        "attacks_on_king": 0.6,
        "passed_pawns":    1.5,
        "weak_squares":    0.9
    },
    "balanced": {
        "material":        1.0,
        "king_safety":     1.0,
        "mobility":        1.0,
        "center_control":  1.0,
        "pawn_chains":     1.0,
        "rook_open_files": 1.0,
        "attacks_on_king": 1.0,
        "passed_pawns":    1.0,
        "weak_squares":    1.0
    },
}
counter_styles = {
    "attacker"  : "defensive",
    "defensive" : "tactical",
    "positional": "attacker",
    "tactical"  : "positional",
    "endgame"   : "attacker",
    "balanced"  : "tactical"
}