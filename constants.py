from enum import StrEnum, IntEnum

MAX_WIDTH = 15_000

MAX_HEIGHT = 15_000

SCALE_FACTOR = 100

BYTES_ON_PIXEL_BY_COLOR_TYPE = {
    0: 1,  # Grayscale
    2: 3,  # Truecolor
    3: 1,  # Indexed-color
    4: 2,  # Grayscale with alpha
    6: 4  # Truecolor with alpha
}


class Modes(StrEnum):
    L = "L"  # Grayscale
    RGB = "RGB"
    Palette = "P"
    RGBA = "RGBA"
    LA = "LA"


class FilterTypes(IntEnum):
    None_ = 0
    Sub = 1
    Up = 2
    Average = 3
    Paeth = 4


class ColorTypes(IntEnum):
    L = 0  # Grayscale
    RGB = 2
    P = 3
    LA = 4
    RGBA = 6
