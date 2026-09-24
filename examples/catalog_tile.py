import sys
from pathlib import Path

from pixops import process

if len(sys.argv) < 2:
    raise SystemExit("usage: python examples/catalog_tile.py product.jpg [out.png]")

src = Path(sys.argv[1])
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(f"{src.stem}_tile.png")
result = process(src, dst, canvas_size=(1000, 1000), background="#FFFFFF")
print(result.output)
