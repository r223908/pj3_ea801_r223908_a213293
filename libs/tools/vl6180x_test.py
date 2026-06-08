from setup import *

while True:
    raw = sensor_tof.range()  # sem filtro, sem offset
    print("RAW:", raw, "mm")
    time.sleep_ms(128)