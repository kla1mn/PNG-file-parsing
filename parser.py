from chunk import Chunk
from ihdr_information import IHDRInformation
from pixel import Pixel


class Parser:
    def __init__(self):
        self.compressed_data_idat = b''
        self.chunks = []

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
        # TODO
        # информация о палитре, в некоторых color_type из IHDR необязательна и в чанках PLTE может не быть.
        # см. https://www.w3.org/TR/png/#11PLTE


        #возможно, надо будет переделать...
        if chunk.length % 3 != 0:
            raise ValueError("Not a valid PNG file (the length of the PLTE data is not a multiple of three)")

        data = chunk.data

        self.pixels: list(Pixel) = []

        for i in range(0, len(data), 3):
            self.pixels.append(Pixel(i // 3, data[i], data[i + 1], data[i + 2]))

    def decompress_data(self):
        # TODO
        # фактически, получение всех пикселей для составления изображения
        pass


if __name__ == '__main__':
    parser = Parser()
    parser.parse("rgb.png")