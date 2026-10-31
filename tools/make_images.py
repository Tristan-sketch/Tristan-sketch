"""Draw every image of this GitHub account in one style.

The look: a dark page with a dot grid, an orange pixel screen and a small
pixel font. One script draws the profile picture,
the banner of the profile README and the banner of each project, so they
always match.

    python tools/make_images.py

Writes into assets/. Copy assets/repos/<name>.png to docs/banner.png of the
matching repository after a change. Needs only the Python standard library.
"""

import struct
import zlib
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

BG = (11, 11, 12)
DOT = (32, 32, 35)
TEXT = (236, 236, 236)
MUTED = (141, 141, 147)
ORANGE = (255, 130, 0)
SCREEN = (255, 138, 0)
INK = (28, 15, 0)

# A 5x7 pixel font with the capitals, digits and the few signs the banners need.
GLYPHS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["#...#", "#...#", "#...#", "#####", "....#", "....#", "....#"],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".....", "..#.."],
    "·": [".....", ".....", ".....", "..#..", ".....", ".....", "....."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
}

# Pixel sprites.
SPRITES = {
    "avatar": [
        ".....######.....",
        "...##########...",
        "..############..",
        "..##.##.##.###..",
        "..#..........#..",
        "..#..........#..",
        "..#..##..##..#..",
        "..#..##..##..#..",
        "..#..........#..",
        "..#..........#..",
        "..#..#....#..#..",
        "..#...####...#..",
        "...#........#...",
        "....########....",
        "......#..#......",
        "..############..",
        ".##############.",
    ],
    # counterfactual-regret: a game tree
    "tree": [
        "....###....",
        "....###....",
        ".....#.....",
        "..#######..",
        "..#.....#..",
        ".###...###.",
        ".###...###.",
        "..#.....#..",
        "#####.#####",
    ],
    # kelly-under-uncertainty: growth rate over the stake, peaking at Kelly
    "curve": [
        ".....#.....",
        "...#####...",
        "..##...##..",
        ".##.....##.",
        ".#.......#.",
        "##.......##",
        "#.........#",
        "...........",
        "###########",
    ],
    # dax-quant-research: a price chart
    "chart": [
        "........###",
        ".........##",
        "....#...#.#",
        "...#.#.#...",
        "..#...#....",
        ".#.........",
        "#..........",
        "...........",
        "###########",
    ],
    # blackjack-counter: a spade
    "spade": [
        "....#....",
        "...###...",
        "..#####..",
        ".#######.",
        "#########",
        "#########",
        ".##.#.##.",
        "....#....",
        "...###...",
    ],
    # BlogPost: a page of text
    "page": [
        "######..",
        "#....##.",
        "#....###",
        "#......#",
        "#.####.#",
        "#......#",
        "#.####.#",
        "#......#",
        "#.###..#",
        "########",
    ],
}

# Every banner: the sprite on the orange screen, a title and one line below it.
BANNERS = {
    "profile": ("avatar", "TRISTAN HARTENSTEIN", "GAME THEORY · PORTFOLIOS · CODE"),
    "kelly-under-uncertainty": ("curve", "KELLY CRITERION", "ESTIMATION RISK · SHRINKAGE · GROWTH"),
    "counterfactual-regret": ("tree", "COUNTERFACTUAL REGRET", "CFR · MCCFR · KUHN · LEDUC"),
    "dax-quant-research": ("chart", "DAX QUANT RESEARCH", "FACTOR STUDY · UPDATED EVERY MONTH"),
    "blackjack-counter": ("spade", "BLACKJACK COUNTER", "WONG HALVES · INDEX PLAYS · ODDS"),
    "BlogPost": ("page", "BLOGPOST", "POSTS · COMMENTS · SESSION AUTH"),
}

for _name, _rows in {**GLYPHS, **SPRITES}.items():
    assert len({len(row) for row in _rows}) == 1, f"'{_name}' has rows of different width"


class Canvas:
    """An RGB image that can fill rectangles and save itself as PNG. Enough for pixel art."""

    def __init__(self, width: int, height: int, color):
        self.width, self.height = width, height
        self.pixels = bytearray(bytes(color) * width * height)

    def rect(self, left: int, top: int, right: int, bottom: int, color, radius: int = 0) -> None:
        """Fill the rectangle including its right and bottom edge, optionally with round corners."""
        for y in range(max(top, 0), min(bottom, self.height - 1) + 1):
            for x in range(max(left, 0), min(right, self.width - 1) + 1):
                if radius and not self._inside_corner(x, y, left, top, right, bottom, radius):
                    continue
                i = (y * self.width + x) * 3
                self.pixels[i : i + 3] = bytes(color)

    @staticmethod
    def _inside_corner(x, y, left, top, right, bottom, radius) -> bool:
        cx = left + radius if x < left + radius else right - radius if x > right - radius else x
        cy = top + radius if y < top + radius else bottom - radius if y > bottom - radius else y
        return (x - cx) ** 2 + (y - cy) ** 2 <= radius**2

    def point(self, x: int, y: int, color) -> None:
        self.rect(x, y, x, y, color)

    def save(self, path: Path) -> None:
        rows = b"".join(
            b"\x00" + bytes(self.pixels[y * self.width * 3 : (y + 1) * self.width * 3])
            for y in range(self.height)
        )

        def chunk(kind: bytes, data: bytes) -> bytes:
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

        header = struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows, 9))
        path.write_bytes(png + chunk(b"IEND", b""))


def draw_rows(draw: Canvas, rows: list[str], x: int, y: int, scale: int, color) -> None:
    """Draw a pixel grid ("#" is filled) with its top left corner at x, y."""
    for row_index, row in enumerate(rows):
        for col_index, pixel in enumerate(row):
            if pixel == "#":
                left, top = x + col_index * scale, y + row_index * scale
                draw.rect(left, top, left + scale - 1, top + scale - 1, color)


def text_width(text: str, scale: int) -> int:
    return (len(text) * 6 - 1) * scale


def draw_text(draw: Canvas, text: str, x: int, y: int, scale: int, color) -> None:
    for i, letter in enumerate(text):
        draw_rows(draw, GLYPHS[letter], x + i * 6 * scale, y, scale, color)


def dot_grid(draw: Canvas, width: int, height: int, color) -> None:
    for x in range(11, width, 22):
        for y in range(11, height, 22):
            draw.point(x, y, color)


def screen_tile(draw: Canvas, sprite: str, x: int, y: int, size: int) -> None:
    """The orange screen with a sprite centred on it, as large as fits."""
    draw.rect(x, y, x + size - 1, y + size - 1, SCREEN, radius=size // 8)
    rows = SPRITES[sprite]
    scale = (size * 2 // 3) // max(len(rows[0]), len(rows))
    sprite_w, sprite_h = len(rows[0]) * scale, len(rows) * scale
    draw_rows(draw, rows, x + (size - sprite_w) // 2, y + (size - sprite_h) // 2, scale, INK)


def make_banner(sprite: str, title: str, subtitle: str, signature: bool) -> Canvas:
    width, height = 1280, 320
    draw = Canvas(width, height, BG)
    dot_grid(draw, width, height, DOT)

    tile = 176
    screen_tile(draw, sprite, 72, (height - tile) // 2, tile)

    # The same title size on every banner, so they look like one series.
    left = 72 + tile + 56
    scale = 7
    assert left + text_width(title, scale) <= width - 72, f"Title too long: {title}"
    draw_text(draw, title, left, 104, scale, TEXT)
    bar_y = 104 + 7 * scale + 22
    draw.rect(left, bar_y, left + 120, bar_y + 6, ORANGE)
    draw_text(draw, subtitle, left, bar_y + 28, 3, ORANGE)

    if signature:
        mark = "TRISTAN-SKETCH"
        draw_text(draw, mark, width - 40 - text_width(mark, 2), height - 40, 2, MUTED)
    return draw


def make_avatar() -> Canvas:
    """Profile picture: the avatar on the orange screen. GitHub crops it to a circle."""
    size = 500
    draw = Canvas(size, size, SCREEN)
    dot_grid(draw, size, size, (240, 122, 0))
    rows = SPRITES["avatar"]
    scale = 17
    sprite_w, sprite_h = len(rows[0]) * scale, len(rows) * scale
    draw_rows(draw, rows, (size - sprite_w) // 2, (size - sprite_h) // 2 + 6, scale, INK)
    return draw


def main() -> None:
    (ASSETS / "repos").mkdir(parents=True, exist_ok=True)
    make_avatar().save(ASSETS / "avatar.png")
    for name, (sprite, title, subtitle) in BANNERS.items():
        is_profile = name == "profile"
        image = make_banner(sprite, title, subtitle, signature=not is_profile)
        target = ASSETS / "banner.png" if is_profile else ASSETS / "repos" / f"{name}.png"
        image.save(target)
    print(f"Images written to {ASSETS}")


if __name__ == "__main__":
    main()
