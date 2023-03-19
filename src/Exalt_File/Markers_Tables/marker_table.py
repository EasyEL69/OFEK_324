from src.Exalt_File.message_ex import Message
from src.Exalt_File.Markers_Tables.Entries.entry import Entry
import struct as s
from typing import Optional

STDOUT_BUFFER_SIZE = 4100


class Marker_Table(Message):
    def __init__(self, begin_string, table_type, entry_size, num_of_entries, end_string, time_tag):
        self.begin_string = begin_string
        self.table_type = table_type
        self.entry_size = entry_size
        self.num_of_entries = num_of_entries
        self.end_string = end_string

        # will be init in subclasses
        self.entries: Optional[list[Entry]] = None
        self.entry_index: int = 0

        # first message header is from adapter 0xFFFC according to Exalt replay file document
        super().__init__(0xFFFC, table_type, time_tag, 0, 0, 0)

    @property
    def format(self) -> str:
        return '>QI{begin_str_len}s3I{data_bytes_len}sI{end_str_len}s'.format(
            begin_str_len=len(self.begin_string.encode('utf-8')),
            data_bytes_len=self.entry_size * self.num_of_entries,
            end_str_len=len(self.end_string.encode('utf-8'))
        )

    def add_entry(self, entry: Entry) -> bool:
        if self.entry_index >= self.num_of_entries:
            # meaning that we can't add new entry to table
            return False

        self.entries[self.entry_index] = entry
        self.entry_index += 1
        return True

    def write_buffer(self):
        if (self.entry_index + 1) * self.entry_size >= STDOUT_BUFFER_SIZE:
            pass


    # TODO: implement the entries array as np.array from
    # TODO: use value.nbytes to evaluate the number of bytes that list is takes
    def pack(self) -> bytes:
        return super().pack() + s.pack(self.format,
                                       self.time_tag,
                                       len(self.begin_string.encode('utf-8')),
                                       self.begin_string.encode('utf-8'),
                                       self.table_type,
                                       self.entry_size,
                                       self.num_of_entries,
                                       b''.join([entry.pack() for entry in self.entries]),
                                       len(self.end_string.encode('utf-8')),
                                       self.end_string.encode('utf-8')
                                       )
