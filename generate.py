import requests
import json

SOURCE = "https://iptv-org.github.io/iptv/countries/it.m3u"


# ---------------------------
# PARSER
# ---------------------------
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


# ---------------------------
# KODI STYLE GROUPING
# ---------------------------
def normalize_name(name):
    n = name.lower()

    if "rai 1" in n:
        return "Rai 1", "RAI"
    if "rai 2" in n:
        return "Rai 2", "RAI"
    if "rai 3" in n:
        return "Rai 3", "RAI"

    if "canale 5" in n:
        return "Canale 5", "MEDIASET"
    if "italia 1" in n:
        return "Italia 1", "MEDIASET"
    if "rete 4" in n:
        return "Rete 4", "MEDIASET"

    if "la7" in n:
        return "La7", "LA7"

    return None, None


# ---------------------------
# MAIN ENGINE
# ---------------------------
def main():
    print("Loading source...")

    r = requests.get(SOURCE, timeout=15)
    channels = parse_m3u(r.text)

    print(f"Raw channels: {len(channels)}")

    tv = {}

    # COSTRUISCE STRUTTURA KODI
    for c in channels:
        norm_name, group = normalize_name(c["name"])

        if not norm_name:
            continue

        if norm_name not in tv:
            tv[norm_name] = {
                "name": norm_name,
                "group": group,
                "sources": []
            }

        tv[norm_name]["sources"].append(c["url"])

    # ORDINE DECODER
    order = [
        "Rai 1",
        "Rai 2",
        "Rai 3",
        "Canale 5",
        "Italia 1",
        "Rete 4",
        "La7"
    ]

    output = {
        "name": "TV Italia Kodi Style Engine",
        "version": "kodi-style",
        "channels": []
    }

    for ch in order:
        if ch in tv:
            output["channels"].append(tv[ch])

    print(f"Final channels: {len(output['channels'])}")

    with open("tvitalia.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
