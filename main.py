#!/usr/bin/env python3
"""Entry point: copy entry.png (same folder) to MAKEFUN_OUTPUT_DIR.

Standard library only. Self-check: the source must be a valid PNG of at
most 1,048,576 bytes; the copy is read back and asserted byte-identical.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    assert data[:8] == PNG_MAGIC, "entry.png is not a valid PNG"
    assert len(data) <= MAX_BYTES, "entry.png exceeds 1,048,576 bytes"
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as f:
        f.write(data)
    with open(out_path, "rb") as f:
        back = f.read()
    assert back == data, "output differs from entry.png"
    assert hashlib.sha256(back).hexdigest() == hashlib.sha256(data).hexdigest()
    print("entry.png written:", out_path, len(data), "bytes")


if __name__ == "__main__":
    main()
