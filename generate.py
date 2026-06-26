import requests
import json

SOURCE = "https://iptv-org.github.io/iptv/countries/it.m3u"

# cache semplice in memoria (durante esecuzione)
alive_cache = {}


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
# CHECK STREAM PIÙ AFFIDABILE (HEAD REQUEST)
# ---------------------------
def is_alive(url):
    if url in alive_cache:
        return alive_cache[url]

    try:
        r = requests.head(url, timeout=3, allow_redirects=True)
        ok = r.status_code < 400
    except:
        ok = False

    alive_cache[url] = ok
    return ok


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
# MAIN SMART+
# ---------------------------
def main():
    print("Downloading IPTV source...")

    r = requests.get(SOURCE, timeout=20)
    channels = parse_m3u(r.text)

    print(f"Raw channels: {len(channels)}")

    tv = {}

    for c in channels:
        name, group = normalize(c["name"])
        if not name:
            continue

        # SMART+: verifica reale HTTP
        if not is_alive(c["url"]):
            continue

        if name not in tv:
            tv[name] = {
                "name": name,
                "group": group,
                "urls": []
            }

        tv[name]["urls"].append(c["url"])

    # ORDINE TIPO DECODER
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
        "name": "TV Italia Smart+ Engine",
        "version": "smart-3.0",
        "channels": []
    }

    for ch in order:
        if ch in tv:
            urls = tv[ch]["urls"]

            # fallback interno (primo valido già filtrato)
            output["channels"].append({
                "name": ch,
                "group": tv[ch]["group"],
                "url": urls[0] if urls else ""
            })

    print(f"Final channels: {len(output['channels'])}")

    with open("tvitalia.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
