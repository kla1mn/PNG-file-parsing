from parser import Parser

parser = Parser()
# parser.parse("images/pizza2.png")
parser.parse("images/cat 1950s vibe.png")
parser.decompress_data()
parser.display_image()