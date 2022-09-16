#!/usr/bin/python3
import time
import struct
import datetime
import serial

# FS-1000 commands
CMD_SET_TIME = 1
CMD_SET_RATIO = 2
CMD_GET_HISTORY_DATA = 3
CMD_DOSE_RATE_THRESHOLD = 4,
CMD_DOSE_THRESHOLD = 5,
CMD_GET_CONFIG = 6
CMD_GET_CUMULATIVE_DOSE = 7

# Packet related stuff
PACKET_START = 0xAA
PACKET_STOP = 0x55
PACKET_ENVELOPE_SIZE = 3

# Serial setup
SERIAL_BAUD = 115200
SERIAL_TIMEOUT = 1


def sp_read_bytes(quantity):
    data = sp.read(quantity)
    if len(data) != quantity:
        raise Exception("Timeout reading from serial port")
    # print(quantity, " ".join(hex(n) for n in data))
    return data


def sp_read_byte():
    return sp_read_bytes(1)[0]


def read_packet():

    # Packet structure:
    #   byte 0xAA (start)
    #   byte length of packet of bytes
    #  ?bytes payload
    #   byte chacksum
    #   byte 0x55 (stop)

    start_marker = sp_read_byte()
    if start_marker != PACKET_START:
        raise Exception("Got malformed packet, wrong 'start' byte")
    length = sp_read_byte()
    payload_length = int(length) - PACKET_ENVELOPE_SIZE
    payload = sp_read_bytes(payload_length)
    checksum = sp_read_byte()
    stop_marker = sp_read_byte()
    if stop_marker != PACKET_STOP:
        raise Exception("Got malformed packet, wrong 'stop' byte")
    return payload


def packet_add_envelope(payload):
    payload_len = len(payload)
    # not sure why not +4 (start(1)-length(2)-..payload..-checksum(3)-stop(4))
    size = PACKET_ENVELOPE_SIZE + payload_len
    checksum = PACKET_START + size
    for byte in payload:
        checksum += byte
    checksum = checksum & 0xFF
    return struct.pack(
        f"cc{payload_len}scc",
        PACKET_START.to_bytes(1, "big"),
        size.to_bytes(1, "big"),
        payload,
        checksum.to_bytes(1, "big"),
        PACKET_STOP.to_bytes(1, "big"),
    )


def sync_time():
    now = time.localtime()
    payload = struct.pack(
        "ccccccc",
        CMD_SET_TIME.to_bytes(1, "big"),
        (now.tm_year - 2000).to_bytes(1, "big"),
        now.tm_mon.to_bytes(1, "big"),
        now.tm_mday.to_bytes(1, "big"),
        now.tm_hour.to_bytes(1, "big"),
        now.tm_min.to_bytes(1, "big"),
        now.tm_sec.to_bytes(1, "big"),
    )
    sp.write(packet_add_envelope(payload))
    response = read_packet()
    return response[0] == CMD_SET_TIME and response[1] == 6


def get_history_data():
    sp.write(packet_add_envelope(CMD_GET_HISTORY_DATA.to_bytes(1, "big")))
    response = read_packet()
    (cmd, status, packets, measurements) = struct.unpack(">BBBH", response)
    if cmd != CMD_GET_HISTORY_DATA or status != 6:
        raise Exception("Read history data failed")
    while packets > 0:
        packet = read_packet()
        packets -= 1
        data = bytearray(packet)
        # remove 'cmd' a 'packet_sequence_number' bytes, don't care about them now
        del data[0:2]
        # 8 bytes per record: 4b encoded date + 4b int32 value
        for i in range(len(data) // 8):
            record = data[i * 8 : i * 8 + 8]
            (t, value) = struct.unpack(">II", record)
            # DateTime format:
            # YYYYYYYM MMMDDDDD HHHHHmmm mmm00000
            year = (t >> 25) + 2000
            month = (t >> 21) & 15
            day = (t >> 16) & 31
            hour = (t >> 11) & 31
            minute = (t >> 5) & 63
            try:
                dt = datetime.datetime(
                    year=year, month=month, day=day, hour=hour, minute=minute
                )
                tsc = dt.timestamp()
                value = value/100
                print(f"{dt}, {int(tsc)}, {value}")
            except Exception as e:
                print(f"Error decoding record: {record.hex(' ', 4)}, => {year}/{month}/{day} {hour}:{minute}")

            measurements -= 1
    return measurements == 0


def read_dose():
    sp.write(packet_add_envelope(CMD_GET_CUMULATIVE_DOSE.to_bytes(1, "big")))
    response = read_packet()
    (cmd, status, value) = struct.unpack(">BBi", response)
    if cmd != CMD_GET_CUMULATIVE_DOSE or status != 6:
        raise Exception("Read cumulative dose failed")
    return value / 100


def read_info():
    sp.write(packet_add_envelope(CMD_GET_CONFIG.to_bytes(1, "big")))
    response = read_packet()
    (
        cmd,
        status,
        dose_rate_thr,
        dose_limit_thr,
        calibr_factor,
        version,
    ) = struct.unpack(">BB5s5sH4s", response)
    if cmd != CMD_GET_CONFIG or status != 6:
        raise Exception("Read info failed")
    return {
        "version": version.decode(),
        "dose_rate_threshold": dose_rate_thr.decode(),
        "dose_limit_threshold": dose_limit_thr.decode(),
        "calibration_factor": int(calibr_factor),
    }


with serial.Serial("/dev/ttyUSB0", SERIAL_BAUD, timeout=SERIAL_TIMEOUT) as sp:
    print("Read info:       ", read_info())
    print("Get history data:", get_history_data())
    print("Cumulative dose: ", read_dose())
    print("Sync time result:", sync_time())
