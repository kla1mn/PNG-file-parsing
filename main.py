from parser import Parser

parser = Parser()
parser.parse("images/originals/pine.png")
parser.decompress_data()
parser.display_image()
