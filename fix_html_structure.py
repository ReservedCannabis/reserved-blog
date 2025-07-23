import os

POST_DIR = "posts"

for filename in os.listdir(POST_DIR):
    if not filename.endswith(".html"):
        continue

    path = os.path.join(POST_DIR, filename)

    with open(path, "r") as f:
        content = f.read()

    if "<body" in content.lower():
        continue  # already fixed

    new_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Reserved Cannabis Article</title>
  <style>
    body {{ background: #000; color: #fff; font-family: Arial, sans-serif; line-height: 1.6; padding: 40px; }}
    a {{ color: #ffd54f; }}
  </style>
</head>
<body>
{content}
</body>
</html>
"""

    with open(path, "w") as f:
        f.write(new_content)

    print(f"✅ Fixed structure in: {filename}")
