class Chunk():
    def __init__(self, length: int, chunk_type: bytes, data: bytes, crc: bytes):
        self.length = length
        self.chunk_type = chunk_type
        self.data = data
        self.crc = crc

    def __str__(self):
        return (f"Length: {self.length} \n"
                f"Chunk Type: {self.chunk_type} \n"
                f"Data size: {len(self.data)} \n"
                f"CRC: {self.crc.hex()} \n")
