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
import files
import config


def import_custom_styles() -> None:
    custom_sytles = files.read_styles_file(config.styles_path)
    if custom_sytles is not None:
        config.styles.update({
            f"Custom_{k}": v for k, v in custom_sytles.items()
        })
    return None

def get_chosen_style() -> dict:
    return config.styles[config.chosen_style]

def available_styles_to_string():
    available_styles = tuple(config.styles.keys())
    stringg = ""
    for name in available_styles:
        stringg += f" var {name}"
    return stringg


if __name__ == "__main__":
    pass