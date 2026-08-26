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
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import chess
import json
import sys
import random
import re
from pathlib import Path


def get_path(path: str,  external: bool = False) -> Path:
    if getattr(sys, 'frozen', False): # PyInstaller
        if external:
            base = Path(sys.executable).parent
        else:
            meipass = getattr(sys, '_MEIPASS', None)
            base = Path(meipass) if meipass else Path(sys.executable).parent
            base = base / "scr"
    else: # CPython
        base = Path(__file__).parent
        if external:
            base = base.parent
    return base / path


def read_opening_book(board_fen) -> chess.Move | None:
    book_path = get_path("data/opening_book.jsonl")
    try:
        f = open(book_path, "r", encoding="utf-8")
    except OSError as e:
        print(f"info string Warning: cannot open the opening_book: {book_path}: {e}", flush=True)
        return None

    target_fen = " ".join(board_fen.split()[:4])
    try:
        with f:
            for line_no, pst in enumerate(f, start=1):
                pst = pst.strip()
                if not pst:
                    continue
                try:
                    data = json.loads(pst)
                    fen = data["fen"]
                    moves = [m["move"] for m in data["top_moves"]]
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"info string opening_book: bad line {line_no}: {e}", flush=True)
                    continue
                if fen == target_fen:
                    return random.choice(moves)
    except OSError as e:
        print(f"info string opening_book: read error: {e}", flush=True)
        return None

    return None


def read_styles_file(path: str) -> dict | None :
    try:
        styles_path = get_path(path, True)
        with open(styles_path, "r", encoding="utf-8") as file:
            custom_styles = json.load(file)
            custom_styles = {
                k: v for k, v in custom_styles.items()
                if not re.fullmatch(r"__comment\d+__", k)
            }
            custom_styles = {
                k: v for k, v in custom_styles.items()
                if v.get("enabled") is not False}
            if custom_styles != {}:
                return custom_styles
            return None
    except FileNotFoundError:
        return None