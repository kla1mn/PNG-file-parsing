from enum import StrEnum

MAX_WIDTH = 15_000

MAX_HEIGHT = 15_000

BYTES_ON_PIXEL_BY_COLOR_TYPE = {
    0: 1,  # Grayscale
    2: 3,  # Truecolor
    3: 1,  # Indexed-color
    4: 2,  # Grayscale with alpha
    6: 4  # Truecolor with alpha
}


class Modes(StrEnum):
    RGB = "RGB",
    Palette = "P",
    RGBA = "RGBA"
