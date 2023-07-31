from pathlib import Path
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

DEBUG = True


def size_to_str(size: int):
    for unit in [" bytes", "KB", "MB", "GB", "TB", "PB", "EB"]:
        if size < 1024:
            break
        size /= 1024
    return f"{size:.2f} {unit}"


def hex_color_str(colors: tuple[int, int, int]) -> str:
    r, g, b, *_ = colors
    return f"\033[48;2;{r};{g};{b}m#{r:02x}{g:02x}{b:02x}\033[0m"


def extract_theme_colors(
    image_path: str,
    num_colors=5,
) -> list[tuple[int, int, int, int]]:
    image_array = np.array(Image.open(image_path).convert("RGBA"))

    k_means = KMeans(n_clusters=num_colors, n_init="auto")
    k_means.fit(image_array.reshape((-1, 4)))

    return k_means.cluster_centers_.astype(int).tolist()


def calc(rgba_color: tuple):
    r, g, b, a, *_ = (*rgba_color, 0xFF)

    diff = (0.299 * r + 0.587 * g + 0.114 * b) * a / 65025
    if DEBUG:
        print(f"{diff: 7.2f}", end=" ")
    return diff


def extract_theme_color(
    image_path: str,
    num_colors=10,
    base_colors: list[tuple[int, int, int, int]] = None,
) -> tuple[int, int, int, int]:
    base_colors = extract_theme_colors(image_path, num_colors)
    colors = list(sorted(base_colors, key=calc))

    if DEBUG:
        print()
        print(" ".join(hex_color_str(color) for color in colors))

    return colors[-1]


if __name__ == "__main__":
    summon_len = 10
    for path in Path().glob("data/**/*"):
        if path.suffix in (".png", ".jpg"):
            print(f'image:"{path}"', size_to_str(path.stat().st_size))

            print(hex_color_str(extract_theme_color(path)))
            print("-" * (summon_len * 8 - 1))
