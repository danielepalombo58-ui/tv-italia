import requests
import json
import socket

SOURCE = "https://iptv-org.github.io/iptv/countries/it.m3u"


# ---------------------------
# PARSER M3U
# ---------------------------
def parse_m3u(content):
    channels = []
    lines = content.splitlines()

    name = None
    for line in lines:
        if line.startswith("#EXTINF"):
            name = line.split(",")[-1].strip()
        elif line.startswith("http") and name:
            channels.append({"name": name, "url": line.strip()})
            name = None
    return channels


# ---------------------------
# SOFT CHECK STREAM (SMART FILTER)
# ---------------------------
def is_alive(url):
    try:
        # check leggerissimo (non scarica tutto)
        host = url.split("/")[2]
        socket.setdefaulttimeout(2)
        socket.socket().connect((host, 80))
        return True
    except:
        return False


# ---------------------------
# NORMALIZZAZIONE CANALI
# ---------------------------
def normalize(name):
    n = name.lower()

    # RAI
    if "rai 1" in n:
        return "Rai 1", "RAI"
    if "rai 2" in n:
        return "Rai 2", "RAI"
    if "rai 3" in n:
        return "Rai 3", "RAI"

    # MEDIASET BASE
    if "canale 5" in n:
        return "Canale 5", "MEDIASET"
    if "italia 1" in n:
        return "Italia 1", "MEDIASET"
    if "rete 4" in n:
        return "Rete 4", "MEDIASET"

    # MEDIASET EXTRA
    if "cine34" in n or "cine 34" in n:
        return "Cine34", "MEDIASET"
    if "iris" in n:
        return "Iris", "MEDIASET"
    if "20 mediaset" in n or "canale 20" in n:
        return "20 Mediaset", "MEDIASET"
    if "top crime" in n:
        return "Top Crime", "MEDIASET"

    # LA7
    if "la7" in n:
        return "La7", "LA7"

    return None, None


# ---------------------------
# MAIN ENGINE SMART
# ---------------------------
def main():
    print("Loading IPTV source...")

    r = requests.get(SOURCE, timeout=20)
    channels = parse_m3u(r.text)

    print(f"Raw channels: {len(channels)}")

    tv = {}

    for c in channels:
        name, group = normalize(c["name"])
        if not name:
            continue

        # SMART FILTER: scarta stream morti
        if not is_alive(c["url"]):
            continue

        if name not in tv:
            tv[name] = {
                "name": name,
                "group": group,
                "url": ""
            }

        if not tv[name]["url"]:
            tv[name]["url"] = c["url"]

    # ORDINE DECODER
    order = [
        "Rai 1",
        "Rai 2",
        "Rai 3",
        "Canale 5",
        "Italia 1",
        "Rete 4",
        "Cine34",
        "Iris",
        "20 Mediaset",
        "Top Crime",
        "La7"
    ]

    output = {
        "name": "TV Italia Smart Engine",
        "version": "smart-2.0",
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
