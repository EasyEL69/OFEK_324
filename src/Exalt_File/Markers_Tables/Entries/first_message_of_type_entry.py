from src.Exalt_File.Markers_Tables.Entries.entry import Entry
import struct as s


class First_Message_Of_Type_Entry(Entry):
    UNSIGNED_LONG = '>I'

    def __init__(self, file_position: int = 0, physical_message_type: int = 0):
        self.physical_message_type = physical_message_type
        super.__init__(file_position)

    def get_size(self) -> int:
        return super().get_size() + s.calcsize(self.UNSIGNED_LONG)

    def pack(self) -> bytes:
        return super().pack() + s.pack(self.UNSIGNED_LONG, self.physical_message_type)
