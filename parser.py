import zlib
from typing import List
from chunk import Chunk
from ihdr_information import IHDRInformation
from plte_information import PLTEInformation
from PIL import Image, ImageFilter
from enum import StrEnum

COLOR_TYPES = {
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


class Parser:
    def __init__(self):
        self.should_blur = False
        self.compressed_data_idat = b''
        self.chunks: List[Chunk] = []
        self.ihdr_information: IHDRInformation
        self.palette: List[PLTEInformation] = []
        self.raw_image = None
        self.image_data = []
        self.pixels = []
        self.mode = None

    def parse(self, file_path: str):
        with open(file_path, 'rb') as file:
            signature = file.read(8)
            if signature != b'\x89PNG\r\n\x1a\n':
                raise ValueError("Не PNG файл, попробуйте другой")

            print(f"Сигнатура: {signature}")
            print()
            self._read_chunks(file)
            print()
            print("Начинаем печатать чанки...\n")
            for chunk in self.chunks:
                print(chunk)
                # input("Нажмите Enter для продолжения \n")

                if chunk.chunk_type == b'IHDR':
                    self._parse_IHDR(chunk)
                elif chunk.chunk_type == b'IDAT':
                    self._parse_IDAT(chunk)
                elif chunk.chunk_type == b'PLTE':
                    self._parse_PLTE(chunk)
                elif chunk.chunk_type == b'tEXt' or chunk.chunk_type == b'iTXt' or chunk.chunk_type == b'zTXt':
                    self._parse_text_chunk(chunk)
                elif chunk.chunk_type == b'IEND':
                    break

            # print(f"Parsed IHDR: {self.ihdr_information}")
            if self.palette:
                print(f"Распарсили PLTE с {len(self.palette)} палитрой.\n")

    def decompress_data(self):
        print("Начинаем декомпрессию IDAT данных...")
        decompressed_data = zlib.decompress(self.compressed_data_idat)
        print(f"Размер декомпрессионных данных: {len(decompressed_data)} байт")

        bytes_per_pixel = self._get_bytes_per_pixel()

        stride = bytes_per_pixel * self.ihdr_information.width
        self.raw_image = []

        i = 0
        for row in range(self.ihdr_information.height):
            if i >= len(decompressed_data):
                raise ValueError("Недостаточно данных изображения.")
            filter_type = decompressed_data[i]  # Каждая строка начинается с байта фильтра
            i += 1
            scanline = decompressed_data[i:i + stride]
            if len(scanline) != stride:
                raise ValueError("Длина сканлайна не соответствует ожидаемому значению.")
            i += stride
            self.raw_image.append((filter_type, scanline))

        print(f"Распарсили {len(self.raw_image)} scanlines.")

        self._apply_filters()
        self._decode_pixels()

    def display_image(self):
        if not self.pixels:
            raise ValueError(
                "Данные изображения не декодированы. Вызовите decompress_data() и decode_pixels() сначала.")

        width = self.ihdr_information.width
        height = self.ihdr_information.height

        print(f"Отображаем изображение: {width}x{height}, режим: {self.mode}")

        if self.mode == "RGB":
            img = self._create_image(height, width, Modes.RGB)
        elif self.mode == "P":
            img = self._create_palette_image(height, width)
        elif self.mode == "RGBA":
            img = self._create_image(height, width, Modes.RGBA)
        else:
            raise NotImplementedError(f"Режим {self.mode} не поддерживается для отображения.")

        if self.should_blur:
            print("Обнаружено '18+' в метаданных. Применяем размытие.")
            img = img.filter(ImageFilter.GaussianBlur(radius=15))

        if width <= 50 or height <= 50:
            img = self._rescale_if_smaller_50px(height, img, width)

        img.show()

    def _read_chunks(self, file):
        while True:
            length_bytes = file.read(4)
            if len(length_bytes) < 4:
                if len(length_bytes) == 0:
                    print("Прочитали все чанки.")
                else:
                    print("У файла в конце чанк битый.")
                break

            length = int.from_bytes(length_bytes, 'big')
            chunk_type = file.read(4)
            data = file.read(length)
            crc = file.read(4)
            self.chunks.append(Chunk(length, chunk_type, data, crc))

    def _parse_IHDR(self, chunk: Chunk):
        data = chunk.data
        self.ihdr_information = IHDRInformation(
            width=int.from_bytes(data[0:4], 'big'),
            height=int.from_bytes(data[4:8], 'big'),
            bit_depth=data[8],
            color_type=data[9],
            compression_method=data[10],
            filter_method=data[11],
            interface_method=data[12]
        )
        print(f"Parsed IHDR: {self.ihdr_information}\n")

    def _parse_IDAT(self, chunk: Chunk):
        self.compressed_data_idat += chunk.data
        print(f"Накопили IDAT информацию: {len(self.compressed_data_idat)} байт.\n")

    def _parse_PLTE(self, chunk: Chunk):
        if self.ihdr_information.color_type != 3:
            print("PLTE чанк найден, но цветовой тип не 3 (Indexed-color). Игнорируем.")
            return

        if chunk.length % 3 != 0:
            raise ValueError("Невалидный PNG файл (длина PLTE информации не кратна трем)")

        data = chunk.data
        self.palette = []

        for i in range(0, len(data), 3):
            self.palette.append(PLTEInformation(i // 3, data[i], data[i + 1], data[i + 2]))

    def _parse_text_chunk(self, chunk: Chunk):
        try:
            data = chunk.data.decode('utf-8')
            keyword, text = data.split('\x00', 1)
            print(f"{keyword}: {text}\n")

            if "18+" in text:
                self.should_blur = True

        except UnicodeDecodeError:
            print("Ошибка декодирования текстового чанка.")
        except ValueError:
            print("Ошибка разбора текстового чанка.")

    def _get_bytes_per_pixel(self):
        color_type = self.ihdr_information.color_type
        bytes_per_pixel = COLOR_TYPES.get(color_type, ValueError(f"Неподдерживаемый цветой тип: {color_type}"))
        return bytes_per_pixel

    def _get_stride(self):
        return self.ihdr_information.width * self._get_bytes_per_pixel()

    def _apply_filters(self):
        print("Применяем фильтры для восстановления пиксельных данных...")
        self.image_data = []
        previous_scanline = bytearray([0] * self._get_stride())

        for idx, (filter_type, scanline) in enumerate(self.raw_image):
            if filter_type == 0:
                # Фильтр None
                recon = bytearray(scanline)
            elif filter_type == 1:
                # Фильтр Sub
                recon = self._filter_sub(scanline, self._get_bytes_per_pixel())
            elif filter_type == 2:
                # Фильтр Up
                recon = self._filter_up(scanline, previous_scanline)
            elif filter_type == 3:
                # Фильтр Average
                recon = self._filter_average(scanline, previous_scanline, self._get_bytes_per_pixel())
            elif filter_type == 4:
                # Фильтр Paeth
                recon = self._filter_paeth(scanline, previous_scanline, self._get_bytes_per_pixel())
            else:
                print(f"Неизвестный тип фильтра: {filter_type}")
                continue

            self.image_data.append(recon)
            previous_scanline = recon

            if (idx + 1) % 100 == 0 or (idx + 1) == len(self.raw_image):
                print(f"Обработано {idx + 1}/{len(self.raw_image)} строк.")

        print("Все фильтры успешно применены.")

    @staticmethod
    def _filter_sub(scanline, bpp):
        recon = bytearray(scanline)
        for i in range(bpp, len(recon)):
            recon[i] = (recon[i] + recon[i - bpp]) % 256
        return recon

    @staticmethod
    def _filter_up(scanline, previous):
        recon = bytearray(scanline)
        for i in range(len(recon)):
            recon[i] = (recon[i] + previous[i]) % 256
        return recon

    @staticmethod
    def _filter_average(scanline, previous, bpp):
        recon = bytearray(scanline)
        for i in range(len(recon)):
            left = recon[i - bpp] if i >= bpp else 0
            up = previous[i]
            recon[i] = (recon[i] + (left + up) // 2) % 256
        return recon

    @staticmethod
    def _filter_paeth(scanline, previous, bpp):
        recon = bytearray(scanline)
        for i in range(len(recon)):
            left = recon[i - bpp] if i >= bpp else 0
            up = previous[i]
            up_left = previous[i - bpp] if i >= bpp else 0
            p = left + up - up_left
            pa = abs(p - left)
            pb = abs(p - up)
            pc = abs(p - up_left)
            if pa <= pb and pa <= pc:
                pr = left
            elif pb <= pc:
                pr = up
            else:
                pr = up_left
            recon[i] = (recon[i] + pr) % 256
        return recon

    def _decode_pixels(self):
        print("Декодируем пиксели из восстановленных данных...")
        # width = self.ihdr_information.width
        # height = self.ihdr_information.height
        color_type = self.ihdr_information.color_type
        bit_depth = self.ihdr_information.bit_depth

        # if bit_depth != 8:
        #    raise NotImplementedError("Поддержка только 8-битной глубины реализована.")

        if color_type == 2:
            # Truecolor (RGB)
            self.mode = "RGB"
            self.pixels = []
            for row in self.image_data:
                row_pixels = []
                for i in range(0, len(row), 3):
                    R, G, B = row[i], row[i + 1], row[i + 2]
                    row_pixels.append((R, G, B))
                self.pixels.append(row_pixels)
            print("Декодировано изображение Truecolor (RGB).")

        elif color_type == 3:
            # Indexed-color (P)
            self.mode = "P"
            if not self.palette:
                raise ValueError("PLTE chunk отсутствует для Indexed-color изображения.")
            # Создаём палитру в формате, который понимает Pillow
            self.pixels = []
            for row in self.image_data:
                self.pixels.append(list(row))  # Индексы палитры
            print("Декодировано изображение Indexed-color.")

        elif color_type == 6:
            # Truecolor with alpha (RGBA)
            self.mode = "RGBA"
            self.pixels = []
            for row in self.image_data:
                row_pixels = []
                for i in range(0, len(row), 4):
                    R, G, B, A = row[i], row[i + 1], row[i + 2], row[i + 3]
                    row_pixels.append((R, G, B, A))
                self.pixels.append(row_pixels)
            print("Декодировано изображение Truecolor с альфа-каналом (RGBA).")
        else:
            raise NotImplementedError(f"Декодирование для цветового типа {color_type} не реализовано.")

    def _create_palette_image(self, height, width):
        img = Image.new("P", (width, height))
        flat_palette = []
        for entry in self.palette:
            flat_palette.extend([entry.R, entry.G, entry.B])
        flat_palette += [0] * (768 - len(flat_palette))
        img.putpalette(flat_palette)
        flat_pixels = [pixel for row in self.pixels for pixel in row]
        img.putdata(flat_pixels)
        return img

    @staticmethod
    def _rescale_if_smaller_50px(height, img, width):
        scale_factor = 100
        new_width = width * scale_factor
        new_height = height * scale_factor
        img = img.resize((new_width, new_height), Image.Resampling.NEAREST)
        return img

    def _create_image(self, height, width, mode):
        img = Image.new(mode, (width, height))
        flat_pixels = [pixel for row in self.pixels for pixel in row]
        img.putdata(flat_pixels)
        return img
