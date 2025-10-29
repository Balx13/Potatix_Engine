import UCI

while True:
    info = ""
    try:
        info = UCI.send_cmd()
    except:
        continue
    if info == "quit":
        break