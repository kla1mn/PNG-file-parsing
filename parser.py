from chunk import Chunk


class Parser:
    def __init__(self):
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

                if chunk.chunk_type == b'IEND':
                    break


if __name__ == '__main__':
    parser = Parser()
    parser.parse("pizza.png")
