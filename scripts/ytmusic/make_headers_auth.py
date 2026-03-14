from pathlib import Path
from ytmusicapi.setup import setup
import re

print("Paste full 'Copy as cURL' command, then press Ctrl-D:")
raw = ""
try:
    while True:
        raw += input() + "\n"
except EOFError:
    pass

headers = []

# -H 'key: value'
for m in re.finditer(r"-H '([^:]+):\s*(.*?)'", raw, re.DOTALL):
    key, value = m.group(1).strip(), m.group(2).strip()
    headers.append(f"{key}: {value}")

# -b 'cookie-string'  -> cookie: ...
m = re.search(r"-b '([^']+)'", raw, re.DOTALL)
if m:
    headers.append(f"cookie: {m.group(1).strip()}")

headers_raw = "\n".join(headers) + "\n"

Path("headers_for_debug.txt").write_text(headers_raw)
setup(filepath="headers_auth.json", headers_raw=headers_raw)
print("Created headers_auth.json")
print("Also wrote normalized headers to headers_for_debug.txt")
