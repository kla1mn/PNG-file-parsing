from parser import Parser


parser = Parser()
parser.parse("images/rgb.png")
parser.decompress_data()
parser.display_image()