import chess

def norm(n) -> float:
    return n / 100

def playing_style_recognition(musters, color):
    color = "white" if color else "black"

    mobility = musters[color]["mobility"]
    rook_open_files_count = musters[color]["rook_open_files_count"]
    attacks_on_king = musters[color]["attacks_on_king"]
    center_control = musters[color]["center_control"]
    king_safety =  musters[color]["king_safety"]
    pawn_chains =  musters[color]["pawn_chains"]
    weak_squares = musters[color]["weak_squares"]
    passed_pawns = musters[color]["passed_pawns"]
    material =     musters[color]["passed_pawns"]

    attack_pref = (
              0.35 * norm(mobility)
            + 0.25 * norm(rook_open_files_count)
            + 0.3  * norm(attacks_on_king)
            + 0.1  * (1 - abs(norm(center_control) - 0.5))
    )

    defense_pref = (
              0.35 * norm(king_safety)
            + 0.25 * norm(center_control)
            + 0.2  * norm(pawn_chains)
            - 0.2  * norm(attacks_on_king)
    )

    positional_pref = (
              0.3  * norm(center_control)
            + 0.25 * (1 - norm(weak_squares))
            + 0.25 * norm(pawn_chains)
            + 0.2  * norm(king_safety)
    )

    tactical_pref = (
              0.4 * norm(mobility)
            + 0.3 * norm(attacks_on_king)
            + 0.2 * norm(rook_open_files_count)
            - 0.1 * norm(center_control)
    )

    endgame_pref = (
              0.4 * norm(passed_pawns)
            + 0.3 * norm(pawn_chains)
            + 0.2 * (1 - abs(norm(material)))
            + 0.1 * (1 - norm(mobility))
    )

    balanced_pref = (
            1 - sum(abs(norm(x) - 0.5) for x in [mobility, center_control, king_safety, pawn_chains]) / 4
    )

    playing_style = max((attack_pref, defense_pref, positional_pref, tactical_pref, endgame_pref, balanced_pref))
    if attack_pref == playing_style:
        return "attacker"
    elif defense_pref == playing_style:
        return "defensive"
    elif positional_pref == playing_style:
        return "positional"
    elif tactical_pref == playing_style:
        return "tactical"
    elif endgame_pref == playing_style:
        return "endgame"
    elif balanced_pref == playing_style:
        return "balanced"
    return ""

sytles = {
    "attacker": {
        "material": 0.85,
        "king_safety": 0.7,
        "mobility": 1.4,
        "center_control": 1.1,
        "pawn_chains": 0.9,
        "rook_open_files": 1.3,
        "attacks_on_king": 1.6,
        "passed_pawns": 0.8,
        "weak_squares": 0.7
    },
    "defensive": {
        "material": 1.2,
        "king_safety": 1.6,
        "mobility": 0.8,
        "center_control": 1.3,
        "pawn_chains": 1.4,
        "rook_open_files": 0.6,
        "attacks_on_king": 0.4,
        "passed_pawns": 1.0,
        "weak_squares": 0.9
    },
    "positional": {
        "material": 1.0,
        "king_safety": 1.2,
        "mobility": 1.0,
        "center_control": 1.5,
        "pawn_chains": 1.3,
        "rook_open_files": 0.9,
        "attacks_on_king": 0.7,
        "passed_pawns": 1.0,
        "weak_squares": 0.6
    },
    "tactical": {
        "material": 0.9,
        "king_safety": 0.8,
        "mobility": 1.5,
        "center_control": 1.0,
        "pawn_chains": 0.8,
        "rook_open_files": 1.4,
        "attacks_on_king": 1.5,
        "passed_pawns": 0.9,
        "weak_squares": 0.8
    },
    "endgame": {
        "material": 1.0,
        "king_safety": 1.0,
        "mobility": 0.8,
        "center_control": 1.1,
        "pawn_chains": 1.3,
        "rook_open_files": 0.8,
        "attacks_on_king": 0.6,
        "passed_pawns": 1.5,
        "weak_squares": 0.9
    },
    "balanced": {
        "material": 1.0,
        "king_safety": 1.0,
        "mobility": 1.0,
        "center_control": 1.0,
        "pawn_chains": 1.0,
        "rook_open_files": 1.0,
        "attacks_on_king": 1.0,
        "passed_pawns": 1.0,
        "weak_squares": 1.0
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