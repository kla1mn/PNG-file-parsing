class Chunk():
    def __init__(self, length: int, chunk_type: bytes, data: bytes,
                 src: bytes):
        self.length = length
        self.chunk_type = chunk_type
        self.data = data
        self.src = src

    def __str__(self):
        return (f"Length: {self.length} \n"
                f"Chunk Type: {self.chunk_type} \n"
                f"Data size: {len(self.data)} \n"
                f"CRC: {self.src.hex()} \n")
