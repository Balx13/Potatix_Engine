"""
This file is part of Potatix Engine
Copyright (C) 2025-2026 Balázs André
Potatix Engine is licensed under a CUSTOM REDISTRIBUTION LICENSE (see LICENCE.txt)
"""

import UCI

def main():
    while True:
        info = UCI.send_cmd()
        if info == "quit":
            return

if __name__ == "__main__":
    main()
else:
    print("Info string Error: The engine did not start. Start the engine as a child process.", flush=True)