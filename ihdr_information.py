class IHDRInformation:
    def __init__(self, width: int, height: int, bit_depth: int,
                 color_type: int, compression_method: int,
                 filter_method: int, interface_method: int):
        self.width = width
        self.height = height
        self.bit_depth = bit_depth
        self.color_type = color_type
        self.compression_method = compression_method
        self.filter_method = filter_method
        self.interface_method = interface_method

    def __str__(self):
        return (f"{self.width}x{self.height} px, bit depth: {self.bit_depth}, color type: {self.color_type}, "
                f"compression: {self.compression_method}, filter: {self.filter_method}")
