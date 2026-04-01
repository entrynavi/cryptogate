#!/usr/bin/env python3
"""
Bluesky自動投稿スクリプト
GitHub Actions から毎日実行、social/latest.txt の内容を投稿
環境変数: BLUESKY_HANDLE, BLUESKY_APP_PASSWORD
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

HANDLE = os.environ.get("BLUESKY_HANDLE", "")
APP_PASSWORD = os.environ.get("BLUESKY_APP_PASSWORD", "")

if not HANDLE or not APP_PASSWORD:
    print("⏭️ BLUESKY_HANDLE / BLUESKY_APP_PASSWORD not set — skipping")
    sys.exit(0)

BASE_URL = "https://bsky.social/xrpc"

def api_call(endpoint, data=None, token=None):
    """AT Protocol API call helper"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data:
        req = urllib.request.Request(url, json.dumps(data).encode(), headers, method="POST")
    else:
        req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# 1. Login (create session)
print(f"🔑 Logging in as {HANDLE}...")
session = api_call("com.atproto.server.createSession", {
    "identifier": HANDLE,
    "password": APP_PASSWORD,
})
token = session["accessJwt"]
did = session["did"]
print(f"✅ Logged in: {did}")

# 2. Read today's post
post_file = "social/latest.txt"
if not os.path.exists(post_file):
    print("⚠️ social/latest.txt not found")
    sys.exit(0)

with open(post_file, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    print("⚠️ Empty post content")
    sys.exit(0)

# 3. Parse facets (links and hashtags)
import re

facets = []

# Detect URLs
for m in re.finditer(r'https?://[^\s]+', text):
    byte_start = len(text[:m.start()].encode("utf-8"))
    byte_end = len(text[:m.end()].encode("utf-8"))
    facets.append({
        "index": {"byteStart": byte_start, "byteEnd": byte_end},
        "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group()}]
    })

# Detect hashtags
for m in re.finditer(r'#(\w+)', text):
    byte_start = len(text[:m.start()].encode("utf-8"))
    byte_end = len(text[:m.end()].encode("utf-8"))
    facets.append({
        "index": {"byteStart": byte_start, "byteEnd": byte_end},
        "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": m.group(1)}]
    })

# 4. Truncate to 300 graphemes (Bluesky limit)
if len(text) > 300:
    text = text[:297] + "..."
    # Recalculate facets for truncated text
    facets = [f for f in facets if f["index"]["byteEnd"] <= len(text.encode("utf-8"))]

# 5. Create post
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
record = {
    "$type": "app.bsky.feed.post",
    "text": text,
    "createdAt": now,
    "langs": ["ja"],
}
if facets:
    record["facets"] = facets

result = api_call("com.atproto.repo.createRecord", {
    "repo": did,
    "collection": "app.bsky.feed.post",
    "record": record,
}, token=token)

print(f"✅ Posted to Bluesky!")
print(f"📝 Length: {len(text)} chars")
print(f"🔗 URI: {result.get('uri', 'N/A')}")
