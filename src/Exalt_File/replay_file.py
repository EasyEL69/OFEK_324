import struct as s


class Header_File:

    @property
    # set gap list position in file
    def gap_list_pos(self) -> int:
        return -1

    @property
    # set mark list position in file
    def mark_list_pos(self) -> int:
        return -1

    def __int__(self, num_of_msgs: int, time_tag: int):
        # Setting header file struct
        self.header_file_format: str = '>37sIi2q'

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
            self.gap_list_pos,
            self.mark_list_pos
        )
