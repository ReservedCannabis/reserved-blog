#!/usr/bin/env python3
from pathlib import Path
import re
import os
from collections import defaultdict

POST_DIRS = [Path("posts"), Path("posts_wrapped")]
DRY_RUN = False  # ← change to False to actually delete

def normalize_slug(name: str) -> str:
    name = name.lower()
    name = name.replace("_", "-")
    name = re.sub(r"-+", "-", name)
    name = re.sub(r"\d+", "", name)
    name = name.replace(".html", "")
    return name.strip("-")

def score(fp: Path) -> int:
    s = 0
    if fp.parent.name == "posts_wrapped":
        s += 100
    if "-" in fp.name and "_" not in fp.name:
        s += 10
    s += int(fp.stat().st_mtime // 1000)
    return s

groups = defaultdict(list)

for root in POST_DIRS:
    if not root.exists():
        continue
    for fp in root.glob("*.html"):
        key = normalize_slug(fp.name)
        groups[key].append(fp)

to_delete = []

for key, files in groups.items():
    if len(files) <= 1:
        continue
    files_sorted = sorted(files, key=score, reverse=True)
    keep = files_sorted[0]
    delete = files_sorted[1:]

    print(f"\n🟢 KEEP: {keep}")
    for d in delete:
        print(f"🔴 DELETE: {d}")
        to_delete.append(d)

print("\n========== SUMMARY ==========")
print(f"Duplicates found: {len(to_delete)}")

if not DRY_RUN:
    for fp in to_delete:
        fp.unlink()
    print("✅ Files deleted.")
else:
    print("⚠️ DRY RUN ONLY — no files deleted")
