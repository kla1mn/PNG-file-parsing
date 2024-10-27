class Parser:
    def read_chunk(self, file):
        length = int.from_bytes(file.read(4), 'big')
        try:
            if length == 0:
                file.read(4 + 4 + 4)
            else:
                print(file.read(4))
                print(file.read(length))
                file.read(4)
        except Exception as e:
            print(e)
        print(length)
        input()

    def parse(self, file_name: str):
        with open(file_name, 'rb') as file:
            signature = file.read(8)
            if b'PNG' not in signature:
                return None
            while file.readable():
                chunk = self.read_chunk(file)


if __name__ == '__main__':
    parser = Parser()
    parser.parse("pizza.png")
