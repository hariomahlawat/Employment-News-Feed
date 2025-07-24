#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import os

# --- Config ---
BASE_URL = "https://dgrindia.gov.in"
PAGE_URL = f"{BASE_URL}/Content1/job-assistance"
OUTPUT_PATH = os.path.join("docs", "feeds", "dgr.xml")

TZ = pytz.timezone("Asia/Kolkata")

# --- Fetch & parse ---
resp = requests.get(PAGE_URL, timeout=15)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

entries = []
for a in soup.select("a"):
    text = a.get_text(strip=True)
    if "Vacancy Notification" in text:
        href = a.get("href")
        url  = requests.compat.urljoin(PAGE_URL, href)
        entries.append({
            "title":   text,
            "url":     url,
            "updated": datetime.now(TZ)
        })

# --- Build Atom feed ---
feed_updated = datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%SZ")
lines = [
    '<?xml version="1.0" encoding="utf-8"?>',
    '<feed xmlns="http://www.w3.org/2005/Atom">',
    f'  <title>DGR Vacancy Notifications</title>',
    f'  <id>{PAGE_URL}</id>',
    f'  <updated>{feed_updated}</updated>',
]

for e in entries:
    updated = e["updated"].strftime("%Y-%m-%dT%H:%M:%SZ")
    lines += [
        '  <entry>',
        f'    <title>{e["title"]}</title>',
        f'    <link href="{e["url"]}" />',
        f'    <id>{e["url"]}</id>',
        f'    <updated>{updated}</updated>',
        f'    <summary>Details at {e["url"]}</summary>',
        '  </entry>',
    ]

lines.append("</feed>")

# --- Write to file ---
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Wrote {len(entries)} entries to {OUTPUT_PATH}")
