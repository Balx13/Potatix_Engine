import threading

stop_event = threading.Event() # Ez tárolja el, hogy az alphabeta-nak van-e még ideje, vagy le kell állni