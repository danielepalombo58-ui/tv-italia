import requests
import json

# 🌐 MULTI SORGENTE (fallback)
SOURCES = [
    "https://iptv-org.github.io/iptv/countries/it.m3u",
    # puoi aggiungerne altre in futuro
]


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
# NORMALIZZAZIONE SMART (LIEVE)
# ---------------------------
def normalize(name):
    n = name.lower()

    # RAI
    if "rai 1" in n or "raiuno" in n:
        return "Rai 1", "RAI"
    if "rai 2" in n or "raidue" in n:
        return "Rai 2", "RAI"
    if "rai 3" in n or "raitre" in n:
        return "Rai 3", "RAI"

    # MEDIASET BASE
    if "canale 5" in n:
        return "Canale 5", "MEDIASET"
    if "italia 1" in n:
        return "Italia 1", "MEDIASET"
    if "rete 4" in n:
        return "Rete 4", "MEDIASET"

    # EXTRA MEDIASET
    if "cine34" in n:
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
# ENGINE MULTI SOURCE
# ---------------------------
def main():
    print("Loading sources...")

    tv = {}

    for src in SOURCES:
        try:
            r = requests.get(src, timeout=20)
            channels = parse_m3u(r.text)

            print(f"Loaded {len(channels)} channels from {src}")

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

                # aggiungiamo fallback URL
                if c["url"] not in tv[name]["urls"]:
                    tv[name]["urls"].append(c["url"])

        except Exception as e:
            print(f"Source error {src}: {e}")

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
        "name": "TV Italia MultiSource Engine",
        "version": "multi-1.0",
        "channels": []
    }

    for ch in order:
        if ch in tv:
            output["channels"].append({
                "name": ch,
                "group": tv[ch]["group"],
                "urls": tv[ch]["urls"]  # 👈 MULTI FALLBACK
            })

    print(f"Final channels: {len(output['channels'])}")

    with open("tvitalia.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
