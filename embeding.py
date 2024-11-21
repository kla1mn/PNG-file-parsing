def embed_png_in_png(container_path: str, hidden_path: str, output_path: str):
    with open(container_path, 'rb') as container_file:
        container_data = container_file.read()

    with open(hidden_path, 'rb') as hidden_file:
        hidden_data = hidden_file.read()

    if not container_data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError("Основной файл не является PNG!")

    if not hidden_data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError("Скрываемый файл не является PNG!")

    iend_index = container_data.rfind(b'IEND')
    if iend_index == -1:
        raise ValueError("Не найден блок IEND в контейнерной PNG!")

    embedded_data = container_data[:iend_index + 8] + hidden_data

    with open(output_path, 'wb') as output_file:
        output_file.write(embedded_data)

    print(f"Скрытая PNG-картинка успешно встроена в {output_path}.")


if __name__ == "__main__":
    embed_png_in_png(
        container_path="images/originals/rgb.png",  # Путь к основной PNG
        hidden_path="images/cat 1950s vibe.png",  # Путь к скрываемой PNG
        output_path="images/test.png"  # Путь для результата
    )
