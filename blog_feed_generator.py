import os
from datetime import datetime

# Directory where your post HTML files live
POSTS_DIR = "posts"
# Output file for your blog feed listing
OUTPUT_FILE = "blog-feed.html"

# Helper to format timestamps
def fmt(ts):
    return datetime.fromtimestamp(ts).strftime("%b %d, %Y")

# Extract title from a post HTML file by reading its <title> tag
# Assumes well-formed HTML with <title>Your Title</title>
def extract_title(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if '<title>' in line:
                start = line.find('<title>') + 7
                end = line.find('</title>')
                return line[start:end].strip()
    # fallback to filename if no title tag
    return os.path.splitext(os.path.basename(path))[0].replace('_', ' ').title()

# Main generation function
def main():
    # Collect all .html files in posts/
    post_files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.html')]
    # Sort by modification time descending
    post_paths = sorted(
        [os.path.join(POSTS_DIR, f) for f in post_files],
        key=lambda p: os.path.getmtime(p),
        reverse=True
    )

    # Start the HTML
    html = [
        '<!doctype html>',
        '<html lang="en">',
        '<head>\n  <meta charset="utf-8">',
        '  <title>Latest Articles</title>\n</head>',
        '<body>',
        '  <h1>Latest Articles</h1>',
        '  <ul>'
    ]

    # Build list items, prefixing each link with posts/
    for path in post_paths:
        fname = os.path.basename(path)
        title = extract_title(path)
        mts = os.path.getmtime(path)
        date = fmt(mts)
        href = f"{POSTS_DIR}/{fname}"
        html.append(f"    <li><a href=\"{href}\">{title}</a> ({date})</li>")

    # Close HTML
    html += [
        '  </ul>',
        '</body>',
        '</html>'
    ]

    # Write out
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(html))
    print(f"✅ {OUTPUT_FILE} written with {len(post_paths)} posts.")

if __name__ == '__main__':
    main()