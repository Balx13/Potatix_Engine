import UCI

while True:
    info = UCI.send_cmd()
    if info == "quit":
        break