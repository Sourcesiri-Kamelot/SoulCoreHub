from time import sleep
from datetime import datetime

while True:
    with open("soul_log.json", "a") as log:
        log.write(f"{datetime.now().isoformat()} - 🫀 SoulCore is alive.\n")
        log.flush()
    sleep(5)
