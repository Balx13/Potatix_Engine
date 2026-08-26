"""
Opening Book Generator for Potatix Engine
"""

"""
This file is part of Potatix Engine
Copyright (C) 2026 Balázs André

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
# (hungarian language)

import asyncio
import chess
import chess.engine
import chess.pgn
import json
import random
import time
import os
from collections import Counter, deque
from typing import Optional

PGN_FILE    = "lichess_elite_database_2021-10.pgn"  # https://database.nikonoel.fr
ENGINE_PATH = "stockfish.exe"                        # https://stockfishchess.org
OUTPUT_FILE = "opening_book.jsonl"

MAX_PLY      = 18    # fél-lépés (18 = 9 teljes lépés)
ENGINE_DEPTH = 20
MULTIPV      = 3
MIN_WORKERS = 4
ENGINE_HASH_MB = 128   # MB / motor-példány
MAX_FENS      = 100_000
MIN_FREQUENCY = 10
CP_TOLERANCE  = 10

NUM_WORKERS    = max(MIN_WORKERS, (os.cpu_count()-2) or 8)
ENGINE_THREADS = max(1, (os.cpu_count() or 8) // NUM_WORKERS)


random.seed(664656540174585650750794237549)
STARTING_NFEN = " ".join(chess.Board().fen().split()[:4])



def normalize_fen(fen: str) -> str:
    return " ".join(fen.split()[:4])


def top_n_for_ply(ply: int, mult: float = 1.0) -> int:
    base = 12 if ply <= 2 else 8 if ply <= 4 else 5 if ply <= 6 else 4 if ply <= 10 else 3
    return max(1, round(base * mult))


def process_pgn() -> dict[str, Counter]:
    print("PGN feldolgozás...", flush=True)
    t0 = time.perf_counter()
    fen_tree: dict[str, Counter] = {}

    with open(PGN_FILE, encoding="utf-8", buffering=1 << 20) as fh:
        while game := chess.pgn.read_game(fh):
            board = game.board()
            prev = STARTING_NFEN
            for ply, move in enumerate(game.mainline_moves(), 1):
                board.push(move)
                nfen = normalize_fen(board.fen())
                fen_tree.setdefault(prev, Counter())[nfen] += 1
                prev = nfen
                if ply >= MAX_PLY:
                    break

    print(f"    {len(fen_tree):,} csomópont  ({time.perf_counter() - t0:.1f}s)\n")
    return fen_tree


def collect_fens(fen_tree: dict, min_freq: int, mult: float) -> set[str]:
    collected: set[str] = {STARTING_NFEN}
    bfs: deque[tuple[str, int]] = deque([(STARTING_NFEN, 0)])

    while bfs and len(collected) < MAX_FENS:
        nfen, ply = bfs.popleft()
        if ply >= MAX_PLY or nfen not in fen_tree:
            continue

        top_n = top_n_for_ply(ply, mult)
        children = [c for c, cnt in fen_tree[nfen].most_common() if cnt >= min_freq][:top_n]
        random.shuffle(children)

        for child in children:
            if child not in collected:
                collected.add(child)
                bfs.append((child, ply + 1))
    return collected


def select_fens(fen_tree: dict) -> list[str]:
    schedule = [
        (MIN_FREQUENCY,              1.0),
        (max(1, MIN_FREQUENCY // 2), 1.2),
        (max(1, MIN_FREQUENCY // 4), 1.5),
        (2,                          2.0),
        (1,                          2.5),
    ]
    print("FEN kiválasztás:")
    result: set[str] = {STARTING_NFEN}
    for min_freq, mult in schedule:
        result = collect_fens(fen_tree, min_freq, mult)
        ok = "✓" if len(result) >= MAX_FENS else " "
        print(f"  [{ok}] min_freq={min_freq:>3}  mult={mult:.1f}  →  {len(result):>7,} FEN")
        if len(result) >= MAX_FENS:
            break

    print(f"\n  Összesen: {len(result):,} FEN  |  Alapállás benne: {STARTING_NFEN in result}\n")
    return list(result)


async def run_analysis(fens: list[str]) -> None:
    total = len(fens)
    done  = 0
    t0    = time.perf_counter()
    limit = chess.engine.Limit(depth=ENGINE_DEPTH)

    engine_q: asyncio.Queue = asyncio.Queue()
    engines: list[chess.engine.Protocol] = []

    for _ in range(NUM_WORKERS):
        _, eng = await chess.engine.popen_uci(ENGINE_PATH)
        await eng.configure({"Threads": ENGINE_THREADS, "Hash": ENGINE_HASH_MB})
        engines.append(eng)
        await engine_q.put(eng)

    async def analyze_one(nfen: str) -> Optional[dict]:
        board = chess.Board(nfen + " 0 1")
        eng   = await engine_q.get()
        try:
            infos = await eng.analyse(board, limit, multipv=MULTIPV)
            if not isinstance(infos, list):
                infos = [infos]

            raw: list[dict] = []
            for info in infos:
                if "pv" not in info or not info["pv"]:
                    continue
                score = info["score"].relative.score(mate_score=10_000)
                if score is not None:
                    raw.append({"move": info["pv"][0].uci(), "score": score})
            if not raw:
                return None
            best = max(m["score"] for m in raw)
            top  = [m for m in raw if m["score"] >= best - CP_TOLERANCE]
            return {"fen": nfen, "top_moves": top}
        except Exception as exc:
            print(f"\n  [HIBA] {nfen[:60]}  →  {exc}")
            return None
        finally:
            await engine_q.put(eng)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        tasks = [asyncio.ensure_future(analyze_one(f)) for f in fens]

        for run in asyncio.as_completed(tasks):
            result = await run
            done  += 1
            elapsed = time.perf_counter() - t0
            rate    = done / elapsed if elapsed > 0 else 0
            eta     = (total - done) / rate if rate > 0 else 0
            print(
                f"\r  [{done:>6}/{total}]  {done / total * 100:5.1f}%  "
                f"{rate:6.1f} állás/s  ETA: {eta:5.0f}s   ",
                end="", flush=True,
            )
            if result:
                out.write(json.dumps(result, ensure_ascii=False) + "\n")

    await asyncio.gather(*(eng.quit() for eng in engines))
    print()


async def main() -> None:
    print(f"Opening Book Generator  |  {NUM_WORKERS} worker  |  depth={ENGINE_DEPTH}\n")
    t_start = time.perf_counter()

    fen_tree = process_pgn()
    fens     = select_fens(fen_tree)

    print(
        f"Elemzés indul  ({NUM_WORKERS} worker × depth {ENGINE_DEPTH}, "
        f"{ENGINE_THREADS} szál/motor, {ENGINE_HASH_MB} MB hash)...\n"
    )
    t_an = time.perf_counter()
    await run_analysis(fens)
    t_end = time.perf_counter()

    print(f"\nKész  →  {OUTPUT_FILE}")
    print(f"  PGN feldolgozás : {t_an  - t_start:>7.1f}s")
    print(f"  Elemzés         : {t_end - t_an   :>7.1f}s  (depth={ENGINE_DEPTH} × {len(fens):,} állás)")
    print(f"  Összesen        : {t_end - t_start:>7.1f}s")
    input("\nNyomj Entert a folytatáshoz...")

if __name__ == "__main__":
    asyncio.run(main())