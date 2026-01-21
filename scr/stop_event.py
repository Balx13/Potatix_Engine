"""
This file is part of Potatix Engine
Copyright (C) 2025-2026 Balázs André
Potatix Engine is licensed under a CUSTOM REDISTRIBUTION LICENSE (see LICENCE.txt)
"""

import threading

stop_event = threading.Event() # Ez tárolja el, hogy az alphabeta-nak van-e még ideje, vagy le kell állni