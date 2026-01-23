# ✅ chain_asin_to_blog.py
import subprocess

print("🔍 Step 1: Fetching ASINs from keywords…")
subprocess.run(["python3", "fetch_reserved_affiliate_products.py"])

print("🔗 Step 2: Populating affiliate links from ASINs…")
subprocess.run(["python3", "populate_affiliate_links.py"])

print("🛒 Step 3: Inserting affiliate products into blog posts…")
subprocess.run(["python3", "affiliate_inserter.py"])

print("✅ ASIN-to-blog product pipeline complete.")


# ✅ Updated run_all.sh (include this in your script)
# Replace individual ASIN steps with:
# python3 chain_asin_to_blog.py
