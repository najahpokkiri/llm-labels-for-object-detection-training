"""Write a deterministic blank PNG to check transport, not detector quality."""
import argparse
import binascii
from pathlib import Path
import struct
import zlib


def blank_png():
    def chunk(kind, data):
        return struct.pack(">I", len(data))+kind+data+struct.pack(">I", binascii.crc32(kind+data)&0xffffffff)
    header = struct.pack(">IIBBBBB", 512, 512, 8, 2, 0, 0, 0)
    rows = (b"\x00" + b"\x80\x80\x80"*512)*512
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR", header)+chunk(b"IDAT", zlib.compress(rows))+chunk(b"IEND", b"")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    with args.output.open("xb") as output:
        output.write(blank_png())
    print("Wrote blank512×512 PNG; not a satellite example or labelled dataset.")
