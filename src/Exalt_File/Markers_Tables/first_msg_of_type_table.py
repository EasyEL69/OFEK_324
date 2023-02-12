from src.Exalt_File.Markers_Tables.marker_table import Marker_Table
from src.Exalt_File.Markers_Tables.Entries.first_message_of_type_entry import First_Message_Of_Type_Entry
from src.Exalt_File.Markers_Tables.Entries.entry import Entry
from typing import Final


class First_Msg_Of_Type_Table(Marker_Table):
    BEGIN_STRING: Final[str] = '-- Begin FirstMsgOfTypeTable'
    END_STRING: Final[str] = '-- End FirstMsgOfTypeTable'
    FIRST_MSG_OF_TYPE_TABLE_TYPE: Final[int] = 1

    def __init__(self, time_tag: int = 0, num_of_entries: int = 0):

        self.table_type: Final[int] = self.FIRST_MSG_OF_TYPE_TABLE_TYPE

        super().__init__(self.BEGIN_STRING, self.table_type, First_Message_Of_Type_Entry().get_size(),
                         num_of_entries, self.END_STRING, time_tag)

        self.entries = [Entry()] * num_of_entries

        for i in (range(len(self.entries))):
            self.entries[i] = First_Message_Of_Type_Entry()
