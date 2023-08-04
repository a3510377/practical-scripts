import shutil
import uuid
from pathlib import Path

import requests

cache = {}


class NULL_NAMESPACE:
    bytes = b""


def online_uuid_to_offline_uuid(online_uuid: str):
    try:
        return cache[online_uuid]
    except KeyError:
        pass

    data: dict = requests.get(
        f"https://api.mojang.com/user/profile/{online_uuid}"
    ).json()

    player_name = data.get("name")
    if player_name:
        offline_uuid = name_to_offline_uuid(player_name)
        print(f"{online_uuid}[{player_name.rjust(20, ' ')}] -> {offline_uuid}")
        player_name = offline_uuid

    cache[online_uuid] = player_name
    return player_name


def name_to_offline_uuid(name: str):
    return uuid.uuid3(NULL_NAMESPACE, f"OfflinePlayer:{name}")


def change_file(file_path: Path, new_name: str) -> None:
    backup_dir = file_path.parent / "online_backup"
    backup_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy(file_path, backup_dir)
    old_file = file_path.with_stem(new_name)
    if old_file.exists():
        (backup_dir / old_file.name).unlink(missing_ok=True)
        shutil.copy(old_file, backup_dir)
        old_file.unlink()

    file_path.rename(old_file)


def parse_file(file: Path):
    try:
        if new_uuid := online_uuid_to_offline_uuid(
            uuid.UUID(file.with_suffix("").name)
        ):
            change_file(file, str(new_uuid))
    except ValueError:
        print(f"Invalid UUID: {file.name}")


# remove old dat files
for file in Path("playerdata").glob("*.dat_old"):
    file.unlink()

for path in ("advancements", "stats"):
    for file in Path(path).glob("*.json"):
        parse_file(file)

for file in Path("playerdata").glob("*.dat"):
    parse_file(file)
