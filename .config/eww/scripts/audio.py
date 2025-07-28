#!/usr/bin/env python3
import subprocess
import sys
import time

while True:
    try:
        vol = subprocess.check_output(["pamixer", "--get-volume"]).decode().strip()
        mute = subprocess.check_output(["pamixer", "--get-mute"]).decode().strip()
        volume = int(vol)
        icon = "" if mute == "true" or volume <= 5 else "" if volume <= 45 else ""
        print(f"{icon} {volume}%")
        sys.stdout.flush()
    except Exception as e:
        print(" ERR", file=sys.stderr)
    finally:
        time.sleep(0.001)
