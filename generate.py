import requests
import json

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
            try:
                name = line.split(",")[-1].strip()
            except:
                name = None
        elif line.startswith("http") and name:
            channels.append({
                "name": name,
                "url": line.strip()
            })
            name = None
    return channels


# ---------------------------
# NORMALIZZAZIONE CANALI
# ---------------------------
def normalize(name):
    n = name.lower()

    # --- RAI ---
    if "rai 1" in n:
        return "Rai 1", "RAI"
    if "rai 2" in n:
        return "Rai 2", "RAI"
    if "rai 3" in n:
        return "Rai 3", "RAI"

    # --- MEDIASET PRINCIPALI ---
    if "canale 5" in n:
        return "Canale 5", "MEDIASET"
    if "italia 1" in n:
        return "Italia 1", "MEDIASET"
    if "rete 4" in n:
        return "Rete 4", "MEDIASET"

    # --- MEDIASET EXTRA ---
    if "cine34" in n or "cine 34" in n:
        return "Cine34", "MEDIASET"
    if "iris" in n:
        return "Iris", "MEDIASET"
    if "20 mediaset" in n or "canale 20" in n:
        return "20 Mediaset", "MEDIASET"
    if "top crime" in n:
        return "Top Crime", "MEDIASET"

    # --- LA7 ---
    if "la7" in n:
        return "La7", "LA7"

    return None, None


# ---------------------------
# MAIN
# ---------------------------
def main():
    print("Downloading IPTV source...")

    r = requests.get(SOURCE, timeout=15)
    channels = parse_m3u(r.text)

    print(f"Raw channels: {len(channels)}")

    tv = {}

    # COSTRUZIONE LISTA
    for c in channels:
        name, group = normalize(c["name"])

        if not name:
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
        # RAI
        "Rai 1",
        "Rai 2",
        "Rai 3",

        # MEDIASET BASE
        "Canale 5",
        "Italia 1",
        "Rete 4",

        # MEDIASET EXTRA
        "Cine34",
        "Iris",
        "20 Mediaset",
        "Top Crime",

        # ALTRO
        "La7"
    ]

    output = {
        "name": "TV Italia Decoder Stable",
        "version": "1.0-mediaset-pack",
        "channels": []
    }

    for ch in order:
        if ch in tv:
            urls = tv[ch]["urls"]

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
