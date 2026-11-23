"""Resumable download of a Synapse file via its pre-signed URL + curl.

Uses the login saved in ~/.synapseConfig. Fetches a fresh pre-signed URL on
every attempt (they expire), resumes with `curl -C -`, and verifies MD5 at the end.
"""
import hashlib
import os
import subprocess
import sys
import time

import synapseclient

SYN_ID = sys.argv[1]
OUT_DIR = sys.argv[2]

syn = synapseclient.Synapse(skip_checks=True, silent=True)
syn.login(silent=True)

ent = syn.get(SYN_ID, downloadFile=False)
handles = syn.restPOST(
    f"/entity/{SYN_ID}/bundle2",
    body='{"includeFileHandles": true}',
)["fileHandles"]
handle = next(h for h in handles if h["id"] == ent.dataFileHandleId)
size, md5, name = int(handle["contentSize"]), handle.get("contentMd5"), ent.name

final = os.path.join(OUT_DIR, name)
part = final + ".part"
# Reuse the earlier synapseclient partial download, if present.
old = [f for f in os.listdir(OUT_DIR) if f.startswith(name + ".synapse_download_")]
if not os.path.exists(part) and old:
    os.replace(os.path.join(OUT_DIR, old[0]), part)

print(f"{name}: {size/1e9:.2f} GB, md5 {md5}", flush=True)

if not os.path.exists(final):
    attempt = 0
    while (os.path.getsize(part) if os.path.exists(part) else 0) < size:
        attempt += 1
        have = os.path.getsize(part) if os.path.exists(part) else 0
        print(f"attempt {attempt}: resuming at {have/1e9:.2f} GB", flush=True)
        url = syn.restGET(f"/entity/{SYN_ID}/file?redirect=false")
        rc = subprocess.call([
            "curl", "-sS", "-L", "-C", "-", "-o", part,
            "--speed-limit", "10000", "--speed-time", "120",
            "--connect-timeout", "30", url,
        ])
        if rc not in (0, 18, 28, 56, 35, 92):
            print(f"curl exit {rc}", flush=True)
        if attempt > 200:
            sys.exit("too many attempts")
        if rc != 0:
            time.sleep(5)
    if os.path.getsize(part) != size:
        sys.exit(f"size mismatch: {os.path.getsize(part)} != {size}")
    os.replace(part, final)

print("downloaded; verifying md5...", flush=True)
h = hashlib.md5()
with open(final, "rb") as f:
    for chunk in iter(lambda: f.read(16 * 1024 * 1024), b""):
        h.update(chunk)
ok = (md5 is None) or (h.hexdigest() == md5)
print(f"md5 {'OK' if ok else 'MISMATCH ' + h.hexdigest()}  ->  {final}", flush=True)
sys.exit(0 if ok else 1)
