"""
This file is part of Potatix Engine
Copyright (C) 2025-2026 Balázs André
Potatix Engine is licensed under a CUSTOM REDISTRIBUTION LICENSE (see LICENCE.txt)
"""

import chess
import chess.polyglot
from collections import namedtuple


TTEntry = namedtuple("TTEntry", ["value", "depth", "flag"])
transposition_table = {}
Max_tt_size = 1_000_000

def store_tt_entry(board, value, depth, flag):
    # Elmenti az állást a TT-be

    key = chess.polyglot.zobrist_hash(board)
    if key in transposition_table:
        old = transposition_table[key]
        if old.depth > depth:
            return
        if old.depth == depth and old.flag == "EXACT" and flag != "EXACT":
            return
        del transposition_table[key]
    if len(transposition_table) >= Max_tt_size:
        del transposition_table[next(iter(transposition_table))]
    transposition_table[key] = TTEntry(value, depth, flag)


def probe_tt(board, depth, alpha, beta):
    # Lekéri a TT-t
    
    key = chess.polyglot.zobrist_hash(board)
    entry = transposition_table.get(key)
    if entry is None or entry.depth < depth:
        return None
    if entry.flag == 'EXACT':
        return entry.value
    elif entry.flag == 'LOWER' and entry.value >= beta:
        return entry.value
    elif entry.flag == 'UPPER' and entry.value <= alpha:
        return entry.value
    return None

