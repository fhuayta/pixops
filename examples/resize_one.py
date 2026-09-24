import sys
from pathlib import Path

from pixops import process

if len(sys.argv) < 2:
    raise SystemExit("usage: python examples/resize_one.py photo.jpg [out.webp]")

src = Path(sys.argv[1])
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(f"{src.stem}_pix.webp")
result = process(src, dst, max_side=1200, quality=80)
print(f"{result.output} ({result.bytes_written} bytes)")
