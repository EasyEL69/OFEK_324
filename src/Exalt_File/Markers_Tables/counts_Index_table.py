from src.Exalt_File.Markers_Tables.marker_table import Marker_Table
from src.Exalt_File.Markers_Tables.Entries.count_index_entry import Count_Index_Entry
from src.Exalt_File.Markers_Tables.Entries.entry import Entry
from typing import Final


class Counts_Index_Table(Marker_Table):
    BEGIN_STRING: Final[str] = '-- Begin CountsIndex'
    END_STRING: Final[str] = '-- End CountsIndex'
    COUNT_INDEX_TABLE_TYPE: Final[int] = 3

    def __init__(self, time_tag: int = 0, num_of_entries: int = 0):

        self.table_type: Final[int] = self.COUNT_INDEX_TABLE_TYPE

        super().__init__(self.BEGIN_STRING, self.table_type, Count_Index_Entry().get_size(),
                         num_of_entries, self.END_STRING, time_tag)

        self.entries = [Entry()] * num_of_entries

        for i in (range(len(self.entries))):
            self.entries[i] = Count_Index_Entry()
