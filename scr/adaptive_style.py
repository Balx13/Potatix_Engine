"""
This file is part of Potatix Engine
Copyright (C) 2025-2026 Balázs André
Potatix Engine is licensed under a CUSTOM REDISTRIBUTION LICENSE (see LICENCE.txt)
"""

import chess
import evaluate
from config import adaptive_style_oppoment_profile
import config


delta_multipliers = {
    "opening":    {"king_safety": 0.5, "mobility": 0.7, "trading": 0.5, "pawns": 0.3, "rook_op_files": 0.2},
    "middlegame": {"king_safety": 5.0, "mobility": 3.0, "trading": 2.0, "pawns": 2.5, "rook_op_files": 4.0},
    "endgame":    {"king_safety": 0.5, "mobility": 1.5, "trading": 6.0, "pawns": 7.0, "rook_op_files": 1.0}
}


def calculate_adaptive_multipliers() -> None:
    # Nem használ minden értéket a kód, de csak úgy van, hátha kell majd
    multipliers = {
        "engine": {
                "mobility": max(1, 2-adaptive_style_oppoment_profile["king_safety"]),
                "rook_op_files": 2 - adaptive_style_oppoment_profile["king_safety"],
                "king_safety": adaptive_style_oppoment_profile["mobility"],
                "pawns": 2-adaptive_style_oppoment_profile["trading"],
                "position_values": max(1, 2-adaptive_style_oppoment_profile["trading"]), #} Csak 1.0-tól, mert érzékeny
                "material": max(1, adaptive_style_oppoment_profile["rook_op_files"]),    #}
                "bishop_pairs": 2-adaptive_style_oppoment_profile["pawns"]
        },
        "oppoment": {
                "mobility":  max(1.0, adaptive_style_oppoment_profile["mobility"]),
                "rook_op_files": adaptive_style_oppoment_profile["rook_op_files"],
                "king_safety": adaptive_style_oppoment_profile["king_safety"],
                "pawns": adaptive_style_oppoment_profile["pawns"],
                "position_values": 1.0, # Itt nincs konkrétum
                "material": max(1, adaptive_style_oppoment_profile["trading"]), #} Csak 1.0-tól, mert érzékeny
                "bishop_pairs": 1.0 # Itt sincs konkrétum
        }
    }
    config.multipliers = multipliers
    return

def reset_multipliers() -> None:
    config.multipliers = {
    "engine": {
        "mobility": 1.0,
        "rook_op_files": 1.0,
        "king_safety": 1.0,
        "pawns": 1.0,
        "position_values": 1.0,
        "material":  1.0,
        "bishop_pairs": 1.0
    },
    "oppoment": {
        "mobility": 1.0,
        "rook_op_files": 1.0,
        "king_safety": 1.0,
        "pawns": 1.0,
        "position_values": 1.0,
        "material":  1.0,
        "bishop_pairs": 1.0
    }
}
    return

def update_oppoment_style(args) -> None:
    board_local = chess.Board()
    for move in args[3:]:
        board_local.push_uci(move)
    engine_turn = board_local.turn
    last_fen = board_local.fen()
    gp = evaluate.game_phase(board_local)

    # Visszalépünk kettőt
    board_local.pop()
    board_local.pop()
    penultimate_fen = board_local.fen()
    board_local.set_fen(chess.STARTING_FEN)

    def get_statistics(fen) -> dict:
        oppoment_turn = not engine_turn
        oppoment_color = chess.WHITE if oppoment_turn else chess.BLACK
        board__ = chess.Board(fen)
        king_safety = evaluate.eval_king_safety(board__, oppoment_color)
        mobility = evaluate.eval_mobility(board__, oppoment_color)
        trading =  evaluate.eval_material(board__, oppoment_color) + mobility # Feszültség = anyag + ütési lehetőségek
        pawns = evaluate.eval_doubled_pawns(board__, oppoment_color) + \
                evaluate.eval_isolated_pawns(board__, oppoment_color) + \
                evaluate.eval_passed_pawns(board__) # Itt nincs konkrét color-mód, de meglátszik a változás
        rook_op_files = evaluate.eval_rook_open_files(board__, oppoment_color)
        return_dict = {
            "king_safety": abs(king_safety),
            "mobility": abs(mobility),
            "trading": abs(trading),
            "pawns": abs(pawns),
            "rook_op_files": abs(rook_op_files)
        }
        return return_dict

    last_datas = get_statistics(last_fen)
    penultimate_datas = get_statistics(penultimate_fen)

    # 1. Delták kiszámítása (Nyers értékek)
    ks_delta = last_datas["king_safety"] - penultimate_datas["king_safety"]
    mb_delta = last_datas["mobility"] - penultimate_datas["mobility"]
    tr_delta = last_datas["trading"] - penultimate_datas["trading"]
    rp_delta = last_datas["rook_op_files"] - penultimate_datas["rook_op_files"]
    pw_delta = last_datas["pawns"] - penultimate_datas["pawns"]

    # 2. Tolerancia
    def apply_tolerance(delta, limit):
        return delta if abs(delta) > limit else 0

    ks_delta = apply_tolerance(ks_delta, 0)
    mb_delta = apply_tolerance(mb_delta, last_datas["mobility"] * 0.15)
    tr_delta = apply_tolerance(tr_delta, 100)
    rp_delta = apply_tolerance(rp_delta, 0)
    pw_delta = apply_tolerance(pw_delta, 10)

    # 3. Fázis alapú korlát és szorzók
    if gp == "opening":
        max_update = 0.05
    elif gp == "middlegame":
        max_update = 0.15
    else:
        max_update = 0.25

    # 4. Frissítés és Clamp
    # Képlet: delta / súly * fázis_szorzó * tanulási_ráta

    updates = {
        "king_safety": (ks_delta / 10) * delta_multipliers[gp]["king_safety"] * 0.02,
        "mobility": (mb_delta / 1.1) * delta_multipliers[gp]["mobility"] * 0.02,
        "trading": (tr_delta / 800) * delta_multipliers[gp]["trading"] * 0.02,
        "pawns": (pw_delta / 40) * delta_multipliers[gp]["pawns"] * 0.02,
        "rook_op_files": (rp_delta / 20) * delta_multipliers[gp]["rook_op_files"] * 0.02
    }
    for key, change in updates.items():
        limited_change = max(-max_update, min(max_update, change))
        new_value = adaptive_style_oppoment_profile[key] + limited_change
        adaptive_style_oppoment_profile[key] = max(0.7, min(1.3, new_value))

    calculate_adaptive_multipliers()
    return

def reset_adaptive_values():
    for key in adaptive_style_oppoment_profile.keys():
        adaptive_style_oppoment_profile[key] = 1.0
    reset_multipliers()
    return