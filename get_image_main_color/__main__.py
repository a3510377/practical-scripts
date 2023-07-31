from pathlib import Path
import random
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans


def size_to_str(size: int):
    for unit in [" bytes", "KB", "MB", "GB", "TB", "PB", "EB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


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


def together(rgba_color, threshold=15, threshold_a=0.4):
    r, g, b, a, *_ = (*rgba_color, 0xFF)

    diff = max(r, g, b) - min(r, g, b)
    return diff <= threshold and (threshold - diff) * a / 0xFF >= threshold_a


def extract_theme_color(
    image_path: str,
    num_colors=10,
    base_colors: list[tuple[int, int, int, int]] = None,
) -> tuple[int, int, int, int]:
    base_colors = extract_theme_colors(image_path, num_colors)
    colors = list(filter(together, base_colors))

    return sorted(colors, key=sum)[-1] if colors else random.choice(base_colors[:-4])


if __name__ == "__main__":
    summon_len = 10
    for path in Path().glob("data/**/*"):
        if path.suffix in (".png", ".jpg"):
            print(f'image:"{path}"', size_to_str(path.stat().st_size))

            print(
                " ".join(hex_color_str(color) for color in extract_theme_colors(path))
            )
            print(hex_color_str(extract_theme_color(path)))
            print("-" * (summon_len * 8 - 1))
