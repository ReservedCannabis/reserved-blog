import json, os

LOG = ".article_log.json"
if not os.path.exists(LOG):
    print("No .article_log.json found — nothing to migrate.")
    raise SystemExit(0)

with open(LOG, "r", encoding="utf-8") as f:
    try:
        data = json.load(f)
    except Exception as e:
        print("Could not read .article_log.json:", e)
        raise SystemExit(1)

# If it's already the new shape, bail out safely
if isinstance(data, dict) and "titles" in data:
    print("Log already in new format — no changes.")
    raise SystemExit(0)

# Old format was a flat list of titles
if isinstance(data, list):
    new_data = {"titles": sorted(set(t.strip() for t in data if isinstance(t, str) and t.strip()))}
else:
    # Unknown shape — keep titles best effort
    titles = []
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                titles.extend([str(x).strip() for x in v])
    new_data = {"titles": sorted(set(t for t in titles if t))}

with open(LOG, "w", encoding="utf-8") as f:
    json.dump(new_data, f, indent=2, ensure_ascii=False)

print(f"Migrated .article_log.json to new format with {len(new_data['titles'])} unique titles.")
