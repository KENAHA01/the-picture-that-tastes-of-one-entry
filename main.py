#!/usr/bin/env python3
"""Entrypoint: copy the prebuilt entry.png into the grader's output dir.

Stdlib only. Self-checks: entry.png must be a valid PNG of at most
1,048,576 bytes; the copy is read back and asserted byte-identical.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUTDIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT = os.path.join(OUTDIR, "entry.png")


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "entry.png is not a PNG"
    assert len(data) <= 1048576, "entry.png is over 1 MiB"
    digest = hashlib.sha256(data).hexdigest()
    os.makedirs(OUTDIR, exist_ok=True)
    with open(OUT, "wb") as f:
        f.write(data)
    with open(OUT, "rb") as f:
        back = f.read()
    assert back == data, "read-back mismatch"
    assert hashlib.sha256(back).hexdigest() == digest, "sha256 mismatch"
    print("entry.png written:", len(data), "bytes, sha256:", digest)


if __name__ == "__main__":
    main()
