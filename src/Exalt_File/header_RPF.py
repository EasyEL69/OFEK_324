import struct as s

UNKNOWN = 0xFFFFFFFF


class Header_RPF:
    def __init__(self, num_of_msgs: int, time_tag: int, gap_list_pos: int = UNKNOWN, mark_list_pos: int = UNKNOWN):
        # Setting header file struct
        self.header_file_format: str = '<37sIL2Q'
        self.init_string: str = 'XCAL Replay file.........Version 2.00'

        self.num_of_msgs: int = num_of_msgs
        self.time_tag: int = time_tag

        self.gap_list_pos = gap_list_pos
        self.mark_list_pos = mark_list_pos

    def set_gap_list_pos(self, gap_list_pos):
        self.gap_list_pos = gap_list_pos

    def set_mark_list_pos(self, mark_list_pos):
        self.mark_list_pos = mark_list_pos

    def get_size(self) -> int:
        return s.calcsize(self.header_file_format)

    def to_pack(self) -> bytes:
        return s.pack(
            self.header_file_format,
            self.init_string.encode('utf-8'),
            self.num_of_msgs,
            self.time_tag,
            self.gap_list_pos,
            self.mark_list_pos
        )
