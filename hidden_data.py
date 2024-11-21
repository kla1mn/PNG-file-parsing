def add_hidden_data_to_png(input_file_path: str, output_file_path: str, hidden_data: bytes):
    with open(input_file_path, 'rb') as input_file:
        png_data = input_file.read()

    iend_marker = b'IEND'
    iend_index = png_data.find(iend_marker)
    if iend_index == -1:
        raise ValueError("Блок IEND не найден в PNG файле.")

    iend_block_end = iend_index + 8
    if len(png_data) < iend_block_end:
        raise ValueError("PNG файл поврежден: некорректный блок IEND.")

    with open(output_file_path, 'wb') as output_file:
        output_file.write(png_data[:iend_block_end])
        output_file.write(hidden_data)
        output_file.write(png_data[iend_block_end:])

    print(f"Скрытая информация добавлена в файл: {output_file_path}")


if __name__ == '__main__':
    input_file = "images/originals/rgb.png"
    output_file = "images/tochka_test.png"
    hidden_data = b"Mozno recomendaciyu v Tochku?"

    add_hidden_data_to_png(input_file, output_file, hidden_data)
