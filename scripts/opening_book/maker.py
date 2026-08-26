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

import asyncio
import json
import os
import random
import time
from collections import Counter, deque

import chess
import chess.engine
import chess.pgn

# beállítások

pgn_file    = "lichess_elite_database_2021-10.pgn"  # https://database.nikonoel.fr
engine_path = "stockfish.exe"                        # https://stockfishchess.org
output_file = "opening_book.jsonl"

max_ply        = 18 # fél-lépés (18 = 9 teljes lépés)
engine_depth   = 20
multipv        = 3
min_workers    = 4
engine_hash_mb = 128 # MB / motor-példány
max_fens       = 100_000
min_frequency  = 10
cp_tolerance   = 10

wide_multipv     = 3 # ennyi jelölt lépést nézünk az első fél-lépésben
wide_ply         = 2
narrow_multipv   = 1  # utána már csak a legjobb lépést

num_workers    = max(min_workers, (os.cpu_count() or 8) - 2)
engine_threads = max(1, (os.cpu_count() or 8) // num_workers)

random.seed(42)

starting_fen = " ".join(chess.Board().fen().split()[:4])


# FEN-fa építése a PGN-ből

def normalize_fen(fen: str) -> str:
    return " ".join(fen.split()[:4])


def build_fen_tree() -> dict[str, Counter]:
    print("PGN feldolgozás...", flush=True)
    t0 = time.perf_counter()
    tree: dict[str, Counter] = {}

    with open(pgn_file, encoding="utf-8", buffering=1 << 20) as fh:
        while game := chess.pgn.read_game(fh):
            board = game.board()
            prev_fen = starting_fen
            for ply, move in enumerate(game.mainline_moves(), 1):
                if ply > max_ply:
                    break
                board.push(move)
                fen = normalize_fen(board.fen())
                tree.setdefault(prev_fen, Counter())[fen] += 1
                prev_fen = fen

    print(f"    {len(tree):,} csomópont  ({time.perf_counter() - t0:.1f}s)\n")
    return tree


# FEN-ek kiválasztása

def branching_factor(ply: int, mult: float) -> int:
    base = 12 if ply <= 2 else 8 if ply <= 4 else 5 if ply <= 6 else 4 if ply <= 10 else 3
    return max(1, round(base * mult))


def collect_fens(tree: dict[str, Counter], min_freq: int, mult: float) -> dict[str, int]:
    collected = {starting_fen: 0}
    queue = deque([(starting_fen, 0)])

    while queue and len(collected) < max_fens:
        fen, ply = queue.popleft()
        if ply >= max_ply or fen not in tree:
            continue

        limit = branching_factor(ply, mult)
        children = [c for c, count in tree[fen].most_common() if count >= min_freq][:limit]
        random.shuffle(children)

        for child in children:
            if child not in collected:
                collected[child] = ply + 1
                queue.append((child, ply + 1))

    return collected


def select_fens(tree: dict[str, Counter]) -> dict[str, int]:
    """Egyre lazább gyakorisági küszöbbel próbálkozik, amíg el nem éri a
    max_fens célszámot, vagy el nem fogynak a lépcsők."""
    schedule = [
        (min_frequency,              1.0),
        (max(1, min_frequency // 2), 1.2),
        (max(1, min_frequency // 4), 1.5),
        (2,                          2.0),
        (1,                          2.5),
    ]

    print("FEN kiválasztás:")
    fens: dict[str, int] = {starting_fen: 0}
    for min_freq, mult in schedule:
        fens = collect_fens(tree, min_freq, mult)
        reached_max = "✓" if len(fens) >= max_fens else " "
        print(f"  [{reached_max}] min_freq={min_freq:>3}  mult={mult:.1f}  →  {len(fens):>7,} FEN")
        if len(fens) >= max_fens:
            break

    print(f"\n  Összesen: {len(fens):,} FEN\n")
    return fens


# motoros elemzés

def multipv_for_ply(ply: int) -> int:
    return wide_multipv if ply < wide_ply else narrow_multipv


async def analyze_fen(fen: str, ply: int, engine: chess.engine.Protocol, limit: chess.engine.Limit) -> dict | None:
    board = chess.Board(fen + " 0 1")
    infos = await engine.analyse(board, limit, multipv=multipv_for_ply(ply))
    if not isinstance(infos, list):
        infos = [infos]

    scored_moves = []
    for info in infos:
        if not info.get("pv"):
            continue
        score = info["score"].white().score(mate_score=10_000)
        if score is not None:
            scored_moves.append((info["pv"][0].uci(), score))

    if not scored_moves:
        return None

    # sötétnél a legjobb lépés a legalacsonyabb (fehér szemszögéből legrosszabb) score
    best_for_side = min(scored_moves, key=lambda m: m[1])[1] if board.turn == chess.BLACK \
        else max(scored_moves, key=lambda m: m[1])[1]

    if board.turn == chess.WHITE:
        top_moves = [move for move, score in scored_moves if score >= best_for_side - cp_tolerance]
    else:
        top_moves = [move for move, score in scored_moves if score <= best_for_side + cp_tolerance]

    return {"fen": fen, "top_moves": top_moves}


async def run_analysis(fens: dict[str, int]) -> None:
    limit = chess.engine.Limit(depth=engine_depth)

    engines = []
    idle_engines: asyncio.Queue = asyncio.Queue()
    for _ in range(num_workers):
        _, engine = await chess.engine.popen_uci(engine_path)
        await engine.configure({"Threads": engine_threads, "Hash": engine_hash_mb})
        engines.append(engine)
        await idle_engines.put(engine)

    async def worker(fen: str, ply: int) -> dict | None:
        engine = await idle_engines.get()
        try:
            return await analyze_fen(fen, ply, engine, limit)
        except Exception as exc:
            print(f"\n  [HIBA] {fen[:60]}  →  {exc}")
            return None
        finally:
            await idle_engines.put(engine)

    total = len(fens)
    done = 0
    t0 = time.perf_counter()

    with open(output_file, "w", encoding="utf-8") as out:
        tasks = [asyncio.ensure_future(worker(fen, ply)) for fen, ply in fens.items()]
        for task in asyncio.as_completed(tasks):
            result = await task
            done += 1
            elapsed = time.perf_counter() - t0
            rate = done / elapsed if elapsed > 0 else 0
            eta = (total - done) / rate if rate > 0 else 0
            print(
                f"\r  [{done:>6}/{total}]  {done / total * 100:5.1f}%  "
                f"{rate:6.1f} állás/s  ETA: {eta:5.0f}s   ",
                end="", flush=True,
            )
            if result:
                out.write(json.dumps(result, ensure_ascii=False) + "\n")

    await asyncio.gather(*(engine.quit() for engine in engines))
    print()


# main

async def main() -> None:
    print(f"Opening Book Generator  |  {num_workers} worker  |  depth={engine_depth}\n")
    t_start = time.perf_counter()

    tree = build_fen_tree()
    fens = select_fens(tree)

    t_analysis_start = time.perf_counter()
    print(
        f"Elemzés indul  ({num_workers} worker × depth {engine_depth}, "
        f"{engine_threads} szál/motor, {engine_hash_mb} MB hash)...\n"
    )
    await run_analysis(fens)
    t_end = time.perf_counter()

    print(f"\nKész  →  {output_file}")
    print(f"  PGN feldolgozás + kiválasztás : {t_analysis_start - t_start:>7.1f}s")
    print(f"  Elemzés                       : {t_end - t_analysis_start:>7.1f}s  (depth={engine_depth} × {len(fens):,} állás)")
    print(f"  Összesen                      : {t_end - t_start:>7.1f}s")
    input("\nNyomj Entert a folytatáshoz...")


if __name__ == "__main__":
    asyncio.run(main())