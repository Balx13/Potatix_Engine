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
