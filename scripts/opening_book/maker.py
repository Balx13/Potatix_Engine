import chess
import chess.engine
import chess.pgn
import json
import random
from collections import Counter


pgn_file = "lichess_elite_database_2021-10.pgn" # Lichess elite database 2021/10 https://database.nikonoel.fr
engine_path = "stockfish_17.1.exe" # Stocckfish 17.1 https://github.com/official-stockfish/Stockfish
output_file = "opening_book.jsonl"

may_ply = 8                  # fél-lépések (8 = 4 teljes lépés)
engine_time = 0.1
multipy = 3

# FEN szelekció szabályok
max_total_fens = 25_000
min_frequency = 5            # ritka folytatások kidobása

random_seed = 92401 # Tényleg csak random gépeltem (enyhe randomizálás)
random.seed(random_seed)
cp_tolerance = 50   # centipawn


def top_n_for_ply(ply: int) -> int:
    # Mélységfüggő fa-szélesség
    if ply <= 2:
        return 12
    elif ply <= 4:
        return 8
    elif ply <= 6:
        return 5
    else:
        return 3

print("PGN feldolgozás indul...")

fen_tree: dict[str, Counter] = {}
root_counter = Counter()

with open(pgn_file, encoding="utf-8") as pgn:
    while True:
        game = chess.pgn.read_game(pgn)
        if game is None:
            break
        board = game.board()
        prev_fen = None

        for ply, move in enumerate(game.mainline_moves(), start=1):
            board.push(move)
            fen = board.fen()
            if prev_fen is not None:
                fen_tree.setdefault(prev_fen, Counter())[fen] += 1
            if ply == 1:
                root_counter[fen] += 1
            prev_fen = fen
            if ply >= may_ply:
                break

print(f"PGN feldolgozás kész. Fa csomópontok: {len(fen_tree)}\n")

final_fens: set[str] = set()

def expand_fen(fen: str, ply: int):
    if ply > may_ply:
        return
    if len(final_fens) >= max_total_fens:
        return
    final_fens.add(fen)
    if fen not in fen_tree:
        return
    top_n = top_n_for_ply(ply)
    next_fens = []
    for next_fen, count in fen_tree[fen].most_common():
        if count < min_frequency:
            break
        next_fens.append(next_fen)
        if len(next_fens) >= top_n:
            break
    random.shuffle(next_fens)
    for next_fen in next_fens:
        expand_fen(next_fen, ply + 1)

# 1. fél-lépés
root_fens = [fen for fen, _ in root_counter.most_common(12)]

for root_fen in root_fens:
    if len(final_fens) >= max_total_fens:
        break
    expand_fen(root_fen, 1)

print(f"Kiválasztott FEN-ek száma: {len(final_fens)}\n")

# Bármilyen UCI sakkmotor jó.
# Én a stockfisht használom, mert a Potatix Engine még túl gyenge ehhez
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

with open(output_file, "w", encoding="utf-8") as out:
    for idx, fen in enumerate(final_fens, start=1):
        print(f"[{idx}/{len(final_fens)}] Elemzés")
        board = chess.Board(fen)
        infos = engine.analyse(
            board,
            chess.engine.Limit(time=engine_time),
            multipv=multipy
        )
        # multipv=1 esetén nincs lista
        if not isinstance(infos, list):
            infos = [infos]
        raw_moves = []

        for info in infos:
            if "pv" not in info or not info["pv"]:
                continue

            score = info["score"].white().score(mate_score=10_000)
            if score is None:
                continue

            raw_moves.append({
                "move": info["pv"][0].uci(),
                "score": score
            })
        if not raw_moves:
            continue
        best_score = max(m["score"] for m in raw_moves)

        filtered_moves = [
            m for m in raw_moves
            if m["score"] >= best_score - cp_tolerance
        ]
        if not filtered_moves:
            filtered_moves = [
                max(raw_moves, key=lambda m: m["score"])
            ]
        record = {
            "fen": fen,
            "top_moves": filtered_moves
        }
        out.write(json.dumps(record, ensure_ascii=False) + "\n")
engine.quit()


print("\nOpening book elkészült")
print(f"Mentve ide: {output_file}")
