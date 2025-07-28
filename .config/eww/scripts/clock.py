#!/usr/bin/env python3
import datetime
import sys

while True:
    try:
        now = datetime.datetime.now()
        print(now.strftime("%I:%M%p"))
        sys.stdout.flush()  # Force immediate output
    except Exception as e:
        print("XX:XX", file=sys.stderr)
    finally:
        import time
        time.sleep(0.1)  # Slightly less than 1s to account for execution time
