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
        transposition_table.popitem()
    transposition_table[key] = TTEntry(value, depth, flag)


def probe_tt(board, depth, alpha, beta):
    key = chess.polyglot.zobrist_hash(board)
    entry = transposition_table.get(key)

    if entry is None or entry.depth < depth:
        return None
    if entry.flag == 'EXACT':
        return entry.value
    if entry.flag == 'LOWER' and entry.value >= beta:
        return entry.value
    if entry.flag == 'UPPER' and entry.value <= alpha:
        return entry.value

    return None

