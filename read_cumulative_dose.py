#!/usr/bin/env python3

"""

Bosean FS-1000 Personal Dosimeter
Read and display cumulative dose in µS

Usage:
    read_cumulative_dose.py [serial_port]

"""

import sys
import struct
import serial


if len(sys.argv) != 2:
    sys.exit(1)

with serial.Serial(sys.argv[1], 115200, timeout=1) as sp:
    sp.write(b"\xAA\x04\x07\xB5U")
    data = sp.read(10)
    (start, _, cmd, status, dose, _, stop) = struct.unpack(">BBBBIBB", data)
    if (start, cmd, status, stop) == (0xAA, 7, 6, 0x55):
        print(dose / 100)
