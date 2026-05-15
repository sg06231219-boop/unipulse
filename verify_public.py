import urllib.request
urls = {
    "health": "http://bore.pub:32930/api/health",
    "universities": "http://bore.pub:32930/api/universities",
    "forum": "http://bore.pub:32930/api/forum/posts?limit=3",
    "frontend": "http://bore.pub:32930/",
}
for name, url in urls.items():
    try:
        r = urllib.request.urlopen(url, timeout=15)
        body = r.read().decode()
        if name == "universities":
            import json
            data = json.loads(body)
            print(f"✅ {name}: {r.status} ({len(data)}所高校)")
        elif name == "frontend":
            print(f"✅ {name}: {r.status} ({len(body)}字节, HTML正常)")
        else:
            print(f"✅ {name}: {r.status} ({body[:100]})")
    except Exception as e:
        print(f"❌ {name}: {e}")