from src.Exalt_File.Markers_Tables.marker_table import Marker_Table
from src.Exalt_File.Markers_Tables.Entries.message_index_entry import Message_Index_Entry
from src.Exalt_File.Markers_Tables.Entries.entry import Entry
from typing import Final


class First_Msg_Of_Type_Table(Marker_Table):
    BEGIN_STRING: Final[str] = '-- Begin MsgIndex'
    END_STRING: Final[str] = '-- End MsgIndex'
    MSG_INDEX_TABLE_TYPE: Final[int] = 0

    def __init__(self, time_tag: int = 0, num_of_entries: int = 0):
        self.table_type: Final[int] = self.MSG_INDEX_TABLE_TYPE

        super().__init__(self.BEGIN_STRING, self.table_type, Message_Index_Entry().get_size(),
                         num_of_entries, self.END_STRING, time_tag)

        self.entries = [Entry()] * num_of_entries

        for i in (range(len(self.entries))):
            self.entries[i] = Message_Index_Entry()

    def pack(self) -> bytes:
        return super().pack().join(entry.pack() for entry in self.entries)
