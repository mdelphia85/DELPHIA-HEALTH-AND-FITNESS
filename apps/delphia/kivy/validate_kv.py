import sys
from pathlib import Path

KV_PATH = Path(__file__).parent / "main.kv"

if not KV_PATH.exists():
    print(f"KV file not found: {KV_PATH}")
    sys.exit(2)

try:
    from kivy.lang import Builder
    Builder.load_file(str(KV_PATH))
    print("KV parsed OK")
    sys.exit(0)
except Exception as e:
    print("KV parse failed:", e)
    sys.exit(1)
