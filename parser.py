from chunk import Chunk
class Parser:
    def read_chunk(self, file):
        length = int.from_bytes(file.read(4), 'big')
        chunk = Chunk(length, file.read(4), file.read(length), file.read(4))
        return chunk

    def parse(self, file_name: str):
        with open(file_name, 'rb') as file:
            signature = file.read(8)
            print(f"Signature: {signature}")
            print()
            if b'PNG' not in signature:
                return None
            while file.readable():
                chunk = self.read_chunk(file)
                print(chunk)
                if chunk.chunk_type == b'IEND':
                    break
                input()

if __name__ == '__main__':
    parser = Parser()
    parser.parse("pizza.png")
