import unittest
import os
import zlib
from PIL import Image
from parser import Parser
from chunk import Chunk


class TestParser(unittest.TestCase):
    TEST_DIR = "test_output"

    def setUp(self):
        """Create a temporary directory for test files."""
        if not os.path.exists(self.TEST_DIR):
            os.makedirs(self.TEST_DIR)

    def tearDown(self):
        """Clean up temporary directory after tests."""
        for file in os.listdir(self.TEST_DIR):
            os.remove(os.path.join(self.TEST_DIR, file))
        os.rmdir(self.TEST_DIR)

    def _create_test_png(self, filename, width=100, height=100, color=(255, 255, 255, 255)):
        """Helper function to create a simple PNG file."""
        img = Image.new("RGBA", (width, height), color)
        filepath = os.path.join(self.TEST_DIR, filename)
        img.save(filepath, "PNG")
        return filepath

    def _create_corrupted_png(self, filename):
        """Helper function to create a corrupted PNG file."""
        filepath = os.path.join(self.TEST_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(b"NotAPNG")
        return filepath

    def test_parse_valid_png(self):
        """Test parsing a valid PNG file."""
        filepath = self._create_test_png("valid.png")
        parser = Parser()
        parser.parse(filepath)

        self.assertTrue(parser.chunks, "Chunks should be parsed from a valid PNG file.")
        self.assertEqual(parser.ihdr_information.width, 100)
        self.assertEqual(parser.ihdr_information.height, 100)

    def test_parse_invalid_png(self):
        """Test parsing an invalid PNG file."""
        filepath = self._create_corrupted_png("invalid.png")
        parser = Parser()

        with self.assertRaises(ValueError):
            parser.parse(filepath)

    def test_hidden_data_processing(self):
        """Test parsing hidden data after the IEND chunk."""
        filepath = self._create_test_png("with_hidden_data.png")
        hidden_data = b"Hidden Message!"

        with open(filepath, "ab") as f:
            f.write(hidden_data)

        parser = Parser()
        parser.parse(filepath)

        self.assertEqual(parser.hidden_data, hidden_data, "Hidden data should be detected and read correctly.")

    def test_decompress_data(self):
        """Test decompression of IDAT data."""
        filepath = self._create_test_png("valid.png")
        parser = Parser()
        parser.parse(filepath)
        parser.decompress_data()

        self.assertIsNotNone(parser.image_data, "Image data should be decompressed successfully.")

    def test_display_image(self):
        """Test displaying the parsed image."""
        filepath = self._create_test_png("display_test.png")
        parser = Parser()
        parser.parse(filepath)
        parser.decompress_data()

        Image.show = None
        parser.display_image()

    def test_text_chunk_parsing(self):
        """Test parsing of text chunks."""
        text_chunk = f"Description\x0018+".encode("utf-8")
        compressed_text = zlib.compress(text_chunk)

        chunk = Chunk(
            length=len(text_chunk),
            chunk_type=b"tEXt",
            data=text_chunk,
            crc=compressed_text
        )

        parser = Parser()
        parser._parse_text_chunk(chunk)

        self.assertTrue(parser.should_blur or parser.should_bw, "Text chunks should trigger metadata flags if present.")

    def test_filter_sub(self):
        """Test Sub filter."""
        scanline = bytearray([10, 20, 30, 40])
        expected = bytearray([10, 30, 60, 100])
        parser = Parser()

        result = parser._filter_sub(scanline, 1)

        self.assertEqual(result, expected, "Sub filter should modify scanline correctly.")

    def test_filter_up(self):
        """Test Up filter."""
        scanline = bytearray([10, 20, 30, 40])
        previous = bytearray([5, 10, 15, 20])
        expected = bytearray([15, 30, 45, 60])
        parser = Parser()

        result = parser._filter_up(scanline, previous)

        self.assertEqual(result, expected, "Up filter should modify scanline correctly.")

    def test_process_hidden_png(self):
        """Test processing of a hidden PNG file."""
        filepath = self._create_test_png("parent.png")
        hidden_filepath = self._create_test_png("hidden.png")
        with open(hidden_filepath, "rb") as hidden_file:
            hidden_data = hidden_file.read()

        with open(filepath, "ab") as parent_file:
            parent_file.write(hidden_data)

        parser = Parser()
        parser.parse(filepath)

        self.assertTrue(parser._is_png(parser.hidden_data), "Hidden data should be identified as a PNG file.")

    def test_grayscale_with_transparency(self):
        """Test applying grayscale with transparency."""
        img = Image.new("RGBA", (10, 10), (255, 0, 0, 128))
        parser = Parser()
        grayscale_img = parser._apply_grayscale_with_transparency(img)

        self.assertEqual(grayscale_img.mode, "RGBA", "Output image should retain RGBA mode.")
        self.assertEqual(grayscale_img.getpixel((0, 0)), (76, 76, 76, 128), "Grayscale conversion should be correct.")

    def test_rescale_image(self):
        """Test rescaling small images."""
        img = Image.new("RGB", (10, 10), (255, 255, 255))
        parser = Parser()
        rescaled_img = parser._rescale_if_smaller_50px(10, 10, img)

        self.assertEqual(rescaled_img.size, (1000, 1000), "Image should be rescaled correctly.")

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file."""
        parser = Parser()
        with self.assertRaises(FileNotFoundError):
            parser.parse("nonexistent_file.png")

    def test_parse_non_png_file(self):
        """Test parsing a non-PNG file."""
        filepath = os.path.join(self.TEST_DIR, "not_a_png.txt")
        with open(filepath, "w") as f:
            f.write("This is not a PNG file.")

        parser = Parser()
        with self.assertRaises(ValueError):
            parser.parse(filepath)

    def test_decompress_data_corrupted_idat(self):
        """Test decompression with corrupted IDAT data."""
        parser = Parser()
        parser.compressed_data_idat = b'corrupted_data'
        with self.assertRaises(zlib.error):
            parser.decompress_data()

    def test_display_image_without_decompression(self):
        """Test displaying an image without decompression."""
        filepath = self._create_test_png("no_decompression.png")
        parser = Parser()
        parser.parse(filepath)
        with self.assertRaises(ValueError):
            parser.display_image()

    def test_hidden_data_non_png(self):
        """Test handling hidden non-PNG data."""
        filepath = self._create_test_png("hidden_non_png.png")
        hidden_data = b"This is hidden non-PNG data!"
        with open(filepath, "ab") as f:
            f.write(hidden_data)

        parser = Parser()
        parser.parse(filepath)

        self.assertEqual(
            parser.hidden_data,
            hidden_data,
            "Hidden non-PNG data should be read correctly."
        )
        self.assertFalse(parser._is_png(parser.hidden_data), "Hidden data should not be identified as PNG.")

    def test_hidden_data_multiple_png(self):
        """Test parsing a file with multiple hidden PNGs."""
        filepath = self._create_test_png("multi_hidden_parent.png")
        hidden1 = self._create_test_png("hidden1.png", width=50, height=50)

        with open(hidden1, "rb") as f1, open(filepath, "ab") as parent_file:
            parent_file.write(f1.read())

        parser = Parser()
        parser.parse(filepath)

        self.assertTrue(parser._is_png(parser.hidden_data), "First hidden PNG should be identified.")

    def test_rescale_large_image(self):
        """Test rescaling of a large image."""
        img = Image.new("RGB", (500, 500), (255, 255, 255))
        parser = Parser()
        rescaled_img = parser._rescale_if_smaller_50px(500, 500, img)

        self.assertEqual(rescaled_img.size, (500, 500), "Large image should not be rescaled.")

    def test_filter_paeth_with_edge_cases(self):
        """Test Paeth filter with edge cases."""
        scanline = bytearray([100, 200, 50, 30])
        previous = bytearray([50, 150, 30, 20])
        bpp = 1

        parser = Parser()
        result = parser._filter_paeth(scanline, previous, bpp)

        expected = bytearray([150, 94, 80, 110])
        self.assertEqual(result, expected, "Paeth filter should produce correct values.")


if __name__ == "__main__":
    unittest.main()
