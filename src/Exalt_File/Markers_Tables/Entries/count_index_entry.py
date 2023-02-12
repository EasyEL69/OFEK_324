from src.Exalt_File.Markers_Tables.Entries.entry import Entry


class Count_Index_Entry(Entry):
    def __init__(self, file_position: int = 0):
        super.__init__(file_position)

    def get_size(self) -> int:
        return super().get_size()

    def pack(self) -> bytes:
        return super().pack()
