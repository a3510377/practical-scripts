from pathlib import Path
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

DEBUG = True


class Color:
    def __init__(self, r: int = 255, g: int = 255, b: int = 255, a: int = 255) -> None:
        self._r, self._g, self._b, self.a = r, g, b, a
        self._brightness: float | None = None

    # fmt: off
    @property
    def r(self) -> int: return self._r # noqa
    @property # noqa
    def g(self) -> int: return self._g # noqa
    @property # noqa
    def b(self) -> int: return self._b # noqa

    def __str__(self) -> str: return self.hex_color # noqa
    def __repr__(self) -> str: return self.hex_color # noqa
    # fmt: on

    @property
    def rgba(self) -> tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)

    @property
    def rgb(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    @property
    def hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @property
    def hex_color(self) -> str:
        return f"\033[48;2;{self.r};{self.g};{self.b}m{self.hex}\033[0m"

    @property
    def brightness(self) -> float:
        if self._brightness is None:
            r, g, b, a = self.rgba

            self._brightness = (0.299 * r + 0.587 * g + 0.114 * b) * a / 65025
        return self._brightness


def size_to_str(size: int):
    for unit in [" bytes", "KB", "MB", "GB", "TB", "PB", "EB"]:
        if size < 1024:
            break
        size /= 1024
    return f"{size:.2f} {unit}"


def extract_theme_colors(
    image_path: str,
    num_colors=5,
) -> list[Color]:
    image_array = np.array(Image.open(image_path).convert("RGBA"))

    k_means = KMeans(n_clusters=num_colors, n_init="auto")
    k_means.fit(image_array.reshape((-1, 4)))

    return [Color(*k) for k in k_means.cluster_centers_.astype(int)]


def extract_theme_color(
    image_path: str,
    num_colors=10,
) -> Color:
    base_colors = extract_theme_colors(image_path, num_colors)
    colors = list(sorted(base_colors, key=lambda x: x.brightness, reverse=True))

    if DEBUG:
        print(" ".join(map(str, colors)))
        for color in colors:
            print(f"{color.brightness: 7.2f}", end=" ")
        print()

    light_color: None
    for color in colors:
        if color.brightness > 0.9:
            light_color = color
        elif color.brightness > 0.2:
            return color
    return light_color or colors[0]


if __name__ == "__main__":
    summon_len = 10
    for path in Path().glob("data/**/*"):
        if path.suffix in (".png", ".jpg"):
            print(f'image:"{path}"', size_to_str(path.stat().st_size))
            print(extract_theme_color(path))
            print("-" * (summon_len * 8 - 1))
