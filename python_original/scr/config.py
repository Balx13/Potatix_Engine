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
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import chess
import threading


stop_event = threading.Event()

MAX_DEPTH = 100
killer_moves = [[] for _ in range(MAX_DEPTH+1)]
history_heuristic = [[[0 for _ in range(64)] for _ in range(64)] for _ in range(6)]
multipv = 1
nodes = 0
engine_turn = True
mate_score = 1_000_000

PIECE_VALUES = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:   0
}


CENTER_SQUARES = [chess.D4, chess.D5, chess.E4, chess.E5]

chosen_style = "None" # None, Attacker, Defender, Positional_player, Dynamic_player, Solid_player,
                     # Endgame_oriented, Counter_attacker, Custom_

styles_path = "custom_styles.json"

styles = {
    "Attacker": {
        "king_safety": 0.8,
        "mobility": 1.30,
        "pawn_structure": 1,
        "rook_files": 1.05,
        "bishop_pair": 1.15,
        "piece_placement": 1.25,
    },

    "Defender": {
        "king_safety": 1.3,
        "mobility": 0.85,
        "pawn_structure": 1.2,
        "rook_files": 0.9,
        "bishop_pair": 0.9,
        "piece_placement": 1.1,
    },

    "Positional_player": {
        "king_safety": 1.2,
        "mobility": 1,
        "pawn_structure": 1.3,
        "rook_files": 1,
        "bishop_pair": 1.1,
        "piece_placement": 1.3,
    },

    "Dynamic_player": {
        "king_safety": 0.9,
        "mobility": 1.3,
        "pawn_structure": 0.9,
        "rook_files": 1.1,
        "bishop_pair": 1.15,
        "piece_placement": 1.25,
    },

    "Solid_player": {
        "king_safety": 1.3,
        "mobility": 0.9,
        "pawn_structure": 1.3,
        "rook_files": 0.95,
        "bishop_pair": 0.9,
        "piece_placement": 1.1,
    },

    "Endgame_oriented": {
        "king_safety": 1.,
        "mobility": 1.15,
        "pawn_structure": 1.25,
        "rook_files": 1.25,
        "bishop_pair": 1.05,
        "piece_placement": 1.2,
    },

    "Counter_attacker": {
        "king_safety": 1.1,
        "mobility": 1.25,
        "pawn_structure": 1.0,
        "rook_files": 1.15,
        "bishop_pair": 1.15,
        "piece_placement": 1.25,
    },

    "None": {
        "king_safety": 1.0,
        "mobility": 1.0,
        "pawn_structure": 1.0,
        "rook_files": 1.0,
        "bishop_pair": 1.0,
        "piece_placement": 1.0,
    }
}

from styles import import_custom_styles
import_custom_styles()


position_values = {
    "opening": {
        chess.PAWN: (
             0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
             5,  5, 10, 25, 25, 10,  5,  5,
             0,  0,  0, 20, 20,  0,  0,  0,
             5, 10,-10,  0,  0,-10, 10,  5,
             5, 10, 10,-20,-20, 10, 10,  5,
             0,  0,  0,  0,  0,  0,  0,  0),
        chess.BISHOP: (
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10, -5,  5, 10, 10,  5, -5,-10,
            -10, -3,  5, 10, 10,  5, -3,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20,),
        chess.KNIGHT: (
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30, -5, 10, 15, 15, 10, -5,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50),
        chess.ROOK: (
             0,  0,  0,  0,  0,  0,  0, 0,
             5, 10, 10, 10, 10, 10, 10, 5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
             0,  0,  0,  5,  5,  0,  0, 0),
        chess.QUEEN: (
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10, -5, -5, -5, -5, -5, -5,-10,
            -10, -5, -5, -5, -5, -5, -5,-10,
            -5,  -5, -3, -5, -5, -3, -5, -5,
             0,  -5, -3, -5, -5, -3, -5, -5,
            -10, -5,  0,  0,  0, -3, -5,-10,
            -10,  0,  0,  5,  5,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20),
        chess.KING: (
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
             20, 20,  0,  0,  0,  0, 20, 20,
             20, 30, 10,  0,  0, 10, 30, 20
        )},
    "middlegame": {
        chess.PAWN: (
             0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
             5,  5, 10, 25, 25, 10,  5,  5,
             0,  0,  0, 20, 20,  0,  0,  0,
             5, 10,-10,  0,  0,-10, 10,  5,
             5, 10, 10,-20,-20, 10, 10,  5,
             0,  0,  0,  0,  0,  0,  0,  0),
        chess.BISHOP: (
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10, -4,  5, 10, 10,  5, -4,-10,
            -10, -3,  5, 10, 10,  5, -3,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20,),
        chess.KNIGHT: (
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30, -4, 10, 15, 15, 10, -4,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50),
        chess.ROOK: (
             0,  0,  0,  0,  0,  0,  0, 0,
             5, 10, 10, 10, 10, 10, 10, 5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
             0,  0,  0,  5,  5,  0,  0, 0),
        chess.QUEEN: (
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -5,   0,  5,  5,  5,  5,  0, -5,
             0,   0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20),
        chess.KING: (
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
             20, 20,  0,  0,  0,  0, 20, 20,
             20, 30, 10,  0,  0, 10, 30, 20)},
    "endgame": {
        chess.PAWN: (
             0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
             5,  5, 10, 25, 25, 10,  5,  5,
             0,  0,  0, 20, 20,  0,  0,  0,
             5, 10,-10,  0,  0,-10, 10,  5,
             5, 10, 10,-20,-20, 10, 10,  5,
             0,  0,  0,  0,  0,  0,  0,  0),
        chess.BISHOP: (
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20,),
        chess.KNIGHT: (
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50),
        chess.ROOK: (
             0,  0,  0,  0,  0,  0,  0, 0,
             5, 10, 10, 10, 10, 10, 10, 5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
            -5,  0,  0,  0,  0,  0,  0,-5,
             0,  0,  0,  5,  5,  0,  0, 0),
        chess.QUEEN: (
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -5,   0,  5,  5,  5,  5,  0, -5,
             0,   0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20),
        chess.KING: (
            -50,-40,-30,-20,-20,-30,-40,-50,
            -30,-20,-10,  0,  0,-10,-20,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-30,  0,  0,  0,  0,-30,-30,
            -50,-30,-30,-30,-30,-30,-30,-50)}
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