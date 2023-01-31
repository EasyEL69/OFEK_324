import src.constants as c
import struct as s


class Entry:
    UNSIGNED_LONG_LONG = '>Q'

    def __init__(self, file_position: int = 0):
        self.file_position = file_position

    def get_size(self) -> int:
        return s.calcsize(self.UNSIGNED_LONG_LONG)

    def pack(self) -> bytes:
        return s.pack(self.UNSIGNED_LONG_LONG, self.file_position)
