import requests
import json

SOURCE = "https://iptv-org.github.io/iptv/countries/it.m3u"

def parse_m3u(content):
    channels = []
    lines = content.splitlines()

    name = None
    for line in lines:
        if line.startswith("#EXTINF"):
            try:
                name = line.split(",")[-1].strip()
            except:
                name = None
        elif line.startswith("http"):
            if name:
                channels.append({
                    "name": name,
                    "url": line.strip()
                })
                name = None
    return channels

def group_channel(name):
    n = name.lower()
    if "rai" in n:
        return "RAI"
    if "canale 5" in n or "italia 1" in n or "rete 4" in n:
        return "MEDIASET"
    if "la7" in n:
        return "LA7"
    if "news" in n:
        return "NEWS"
    return "ITALIA"

def main():
    r = requests.get(SOURCE)
    raw = r.text

    channels = parse_m3u(raw)

    output = {
        "name": "TV Italia Full",
        "version": "auto",
        "source": SOURCE,
        "channels": []
    }

    seen = set()

    for c in channels:
        key = c["name"].lower()
        if key in seen:
            continue
        seen.add(key)

        output["channels"].append({
            "name": c["name"],
            "url": c["url"],
            "group": group_channel(c["name"])
        })

    with open("tvitalia.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
