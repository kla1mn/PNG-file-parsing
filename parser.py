import zlib
from typing import List
from chunk import Chunk
from ihdr_information import IHDRInformation
from plte_information import PLTEInformation
import tkinter as tk

COLOR_TYPES = {
    0: 1,
    2: 3,
    3: 1,
    4: 2,
    6: 4
}


class Parser:
    def __init__(self):
        self.compressed_data_idat = b''
        self.chunks = []
        self.ihdr_information = None
        self.palette: List[PLTEInformation] = []
        self.raw_image = None

    def read_chunks(self, file):
        while True:
            length_bytes = file.read(4)
            if len(length_bytes) < 4:
                if len(length_bytes) == 0:
                    print("Прочитали")
                else:
                    print("у файла в конце чанк битый")
                break

            length = int.from_bytes(length_bytes, 'big')
            chunk_type = file.read(4)
            data = file.read(length)
            crc = file.read(4)
            self.chunks.append(Chunk(length, chunk_type, data, crc))

    def parse(self, file_path: str):
        with open(file_path, 'rb') as file:
            signature = file.read(8)
            if signature != b'\x89PNG\r\n\x1a\n':
                raise ValueError("Not a valid PNG file")

            print(f"Signature: {signature}")
            print()

            print("Начинаем читать чанки...")
            self.read_chunks(file)

            print()

            print("Начинаем печатать чанки...")
            for chunk in self.chunks:
                print(chunk)
                input("Нажмите Enter для продолжения \n")

                if chunk.chunk_type == b'IHDR':
                    self.parse_IHDR(chunk)
                elif chunk.chunk_type == b'IDAT':
                    self.parse_IDAT(chunk)
                elif chunk.chunk_type == b'PLTE':
                    self.parse_PLTE(chunk)

                elif chunk.chunk_type == b'IEND':
                    break

    def parse_IHDR(self, chunk: Chunk):
        data = chunk.data
        self.ihdr_information = IHDRInformation(int.from_bytes(data[0:4], 'big'),
                                                int.from_bytes(data[4:8], 'big'),
                                                data[8], data[9],
                                                data[10], data[11], data[12])

    def parse_IDAT(self, chunk: Chunk):
        self.compressed_data_idat += chunk.data

    def parse_PLTE(self, chunk: Chunk):

        if chunk.length % 3 != 0:
            raise ValueError("Not a valid PNG file (the length of the PLTE data is not a multiple of three)")

        data = chunk.data
        self.palette = []

        for i in range(0, len(data), 3):
            self.palette.append(PLTEInformation(i // 3, data[i], data[i + 1], data[i + 2]))

    def decompress_data(self):
        decompressed_data = zlib.decompress(self.compressed_data_idat)

        bytes_per_pixel = self.get_bytes_per_pixel()

        # Смотрим сколько пикселей в строке и умножаем на число байт, чтобы получить, сколько байт в строке
        stride = bytes_per_pixel * self.ihdr_information.width
        self.raw_image = []

        i = 0
        # добавляем в сырое изображение строку вместе со своим фильтром, чтобы потом применить фильтр к каждой строке
        for row in range(self.ihdr_information.height):
            filter_type = decompressed_data[i]  # (каждая строка начинается с байта фильтра)
            i += 1
            scanline = decompressed_data[i:i + stride]
            i += stride
            self.raw_image.append((filter_type, scanline))

        print(f"Parsed {len(self.raw_image)} scanlines.")

        # Применение фильтров для восстановления пиксельных данных
        # self.apply_filters() TODO

    def get_bytes_per_pixel(self): 
        color_type = self.ihdr_information.color_type
        return COLOR_TYPES.get(color_type, ValueError(f"Unsupported color type: {color_type}"))
        # if color_type == 0:  # Grayscale
        #     return 1
        # elif color_type == 2:  # Truecolor
        #     return 3
        # elif color_type == 3:  # Indexed-color
        #     return 1
        # elif color_type == 4:  # Grayscale with alpha
        #     return 2
        # elif color_type == 6:  # Truecolor with alpha
        #     return 4
        # else:
        #     raise ValueError(f"Unsupported color type: {color_type}")

    def display_image(self):
        pass


if __name__ == '__main__':
    parser = Parser()
    parser.parse("rgb.png")
    parser.decompress_data()
    parser.display_image()
