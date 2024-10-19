

def parse(file_name: str):
    with open(file_name, 'rb') as file:
        signature = file.read(8)
        if b'PNG' not in signature:
            return None
        print('ok')


if __name__ == '__main__':
    parse("pizza.png")
    parse("pizza.jpeg")
