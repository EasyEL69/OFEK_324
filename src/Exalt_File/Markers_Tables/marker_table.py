from src.Exalt_File.message_ex import Message
import src.constants as c
from src.Exalt_File.Markers_Tables.Entries.entry import Entry
import struct as s


class Marker_Table(Message):
    def __init__(self, begin_string, table_type, entry_size, num_of_entries, end_string, time_tag):
        self.begin_string = begin_string
        self.table_type = table_type
        self.entry_size = entry_size
        self.num_of_entries = num_of_entries
        self.end_string = end_string

        # will be init in subclasses
        self.entries: list[Entry] = None
        self.entry_index = 0

        # first message header is from adapter 0xFFFC according to Exalt replay file document
        super().__init__(0xFFFC, table_type, time_tag, 0, 0, 0, c.FIX_MSG_START)

    @property
    def format(self) -> str:
        return '>QI{begin_str_len}s3I{data_bytes_len}BI{end_str_len}s'.format(
            begin_str_len=len(self.begin_string),
            data_bytes_len=self.entry_size * self.num_of_entries,
            end_str_len=len(self.end_string)
        )

    def add_entry(self, entry: Entry) -> bool:
        if self.entry_index >= self.num_of_entries:
            # meaning that we can't add new entry to table
            return False

        self.entries[self.entry_index] = entry
        self.entry_index += 1
        return True

    def pack(self) -> bytes:
        return super().pack() + s.pack(self.format,
                                       self.time_tag,
                                       len(self.begin_string),
                                       self.begin_string.encode('utf-8'),
                                       self.table_type,
                                       self.entry_size,
                                       self.num_of_entries,
                                       *[entry.pack() for entry in self.entries],
                                       len(self.end_string),
                                       self.end_string.encode('utf-8')
                                       )
