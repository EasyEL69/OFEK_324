import struct as s


class Header_RPF:

    @property
    # set gap list position in file
    def gap_list(self) -> int:
        return 0

    @property
    # set mark list position in file
    def mark_list(self) -> int:
        return 0

    def __init__(self, num_of_msgs: int, time_tag: int):
        # Setting header file struct
        self.header_file_format: str = '<37sIL2Q'

        self.init_string: str = 'XCAL Replay file.........Version 2.00'
        self.num_of_msgs: int = num_of_msgs
        self.time_tag: int = time_tag

    # ----------------------- dynamic data from here --------------------------------------
    def to_pack(self) -> bytes:
        return s.pack(
            self.header_file_format,
            self.init_string.encode('utf-8'),
            self.num_of_msgs,
            self.time_tag,
            self.gap_list,
            self.mark_list
        )
