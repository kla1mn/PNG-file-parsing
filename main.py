from parser import Parser

parser = Parser()
# parser.parse("images/pizza2.png")
parser.parse("images/cat 18+.png")
parser.decompress_data()
parser.display_image()
