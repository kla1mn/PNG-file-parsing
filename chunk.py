class Chunk():
    def __init__(self, length, chunk_type, data, src):
        self.length = length
        self.chunk_type = chunk_type
        self.data = data
        self.src = src

    def __str__(self):
        return (f"Length: {self.length} \n"
              f"Chunk Type: {self.chunk_type} \n"
              f"Data: {self.data} \n"
              f"Src: {self.src}")
