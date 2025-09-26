import chess
import chess.polyglot
from collections import namedtuple

# Transposition table bejegyzés típusa
TTEntry = namedtuple("TTEntry", ["value", "depth", "flag"])
transposition_table = {}

# Transposition table mentése
def store_tt_entry(board, value, depth, flag):
    key = chess.polyglot.zobrist_hash(board)
    if key in transposition_table:
        old = transposition_table[key]
        if old.depth > depth:
            return
        if old.depth == depth and old.flag == "EXACT" and flag != "EXACT":
            return
    transposition_table[key] = TTEntry(value, depth, flag)

# Transposition table lekérdezése
def probe_tt(board, depth, alpha, beta):
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

