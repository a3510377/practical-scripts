import re
from pathlib import Path

import requests

UUID_MATCH = re.compile(
    r"([0-9a-f]{8})(?:-|)([0-9a-f]{4})(?:-|)"
    r"(4[0-9a-f]{3})(?:-|)([89ab][0-9a-f]{3})(?:-|)([0-9a-f]{12})"
)


if __name__ == "__main__":
    names = Path("./names.txt").read_text(encoding="utf-8").splitlines()
    names_map: dict[str, str | None] = {}  # dict[uuid, name]
    miss_id = []

    for name in names:
        name = name.strip()
        if UUID_MATCH.match(name):
            names_map[name] = None
            continue
        else:
            miss_id.append(name)

    if miss_id:
        for i in range(0, len(miss_id), 10):
            data = miss_id[i : i + 10]
            r = requests.post("https://api.mojang.com/profiles/minecraft", json=data)
            if r.status_code == 200:
                for uuid in r.json():
                    names_map[uuid["id"]] = uuid["name"]
            else:
                print("錯誤無法獲取 UUID: ", data)

    for uuid, name in names_map.items():
        if name is None:
            r = requests.get(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
            )

            if r.status_code == 200:
                name = r.json()["name"]
                names_map[uuid] = name
            else:
                print("錯誤無法獲取該 UUID 所有者: ", uuid, r.status_code)

        # r = requests.get(f"https://crafatar.com/avatars/{uuid}?size=128")
        r = requests.get(f"https://mineskin.eu/helm/{name}")
        if r.status_code == 200:
            file = Path(f"./avatars/{name}.png")
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(r.content)
        else:
            print("無法取該 UUID 頭像: ", uuid, r.status_code)
