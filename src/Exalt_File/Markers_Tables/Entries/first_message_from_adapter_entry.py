from src.Exalt_File.Markers_Tables.Entries.entry import Entry
import src.constants as c
import struct as s


class First_Message_From_Adapter_Entry(Entry):
    UNSIGNED_SHORT = '<H'

    def __init__(self, file_position: int = 0, adapter_id: int = 0):
        self.adapter_id = adapter_id
        super.__init__(file_position)

    def get_size(self) -> int:
        return super().get_size() + s.calcsize(self.UNSIGNED_SHORT)

    def pack(self) -> bytes:
        return super().pack() + s.pack(self.UNSIGNED_SHORT, self.adapter_id)
