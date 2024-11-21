import json

from PIL import Image, PngImagePlugin


def add_metadata_to_png(input_file_path, output_file_path, metadata):
    img = Image.open(input_file_path)
    meta = PngImagePlugin.PngInfo()
    meta.add_itxt('Json metadata', json.dumps(metadata, ensure_ascii=False))
    img.save(output_file_path, "PNG", pnginfo=meta)
    print(f"Метаданные успешно добавлены в файл {output_file_path}")


if __name__ == "__main__":
    metadata = {
        "Warning": "18+"
    }
    input_file = "images/filters/cat.png"
    output_file = "images/filters/cat 18+.png"
    add_metadata_to_png(input_file, output_file, metadata)
