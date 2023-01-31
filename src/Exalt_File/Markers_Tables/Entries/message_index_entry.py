from src.Exalt_File.Markers_Tables.Entries.entry import Entry
import struct as s


class Message_Index_Entry(Entry):
    UNSIGNED_LONG_LONG = '>Q'

    def __init__(self, file_position, time_tag):
        self.time_tag = time_tag
        super.__init__(file_position)

    def get_size(self) -> int:
        return super().get_size() + s.calcsize(self.UNSIGNED_LONG_LONG)

    def pack(self) -> bytes:
        return super().pack() + s.pack(self.UNSIGNED_LONG_LONG, self.time_tag)
