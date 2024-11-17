class IHDRInformation:
    def __init__(self, width: int, height: int, bit_depth: bytes,
                 color_type: bytes, compression_method: bytes,
                 filter_method: bytes, interface_method: bytes):
        self.width = width
        self.height = height
        self.bit_depth = bit_depth
        self.color_type = color_type
        self.compression_method = compression_method
        self.filter_method = filter_method
        self.interface_method = interface_method