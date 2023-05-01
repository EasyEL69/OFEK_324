import functools
import struct as s
from typing import Optional, Final, BinaryIO

BASE_HEX: Final[int] = 16
DEFAULT_VALUE: Final[int] = 0x00000000  # 0xFFFFFFFF


def convert_string_to_integer():
    def convert_string_to_integer_inner(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            args_converted = [int(val, BASE_HEX) if isinstance(val, str) and val != 'Msg Error' else val for val in
                              args]
            kwargs_converted = {key: int(val, BASE_HEX) if isinstance(val, str) and val != 'Msg Error' else val for
                                key, val in kwargs.items()}
            return func(*args_converted, **kwargs_converted)

        return wrapped

    return convert_string_to_integer_inner


def convert_optional_none_to(default_value=0x0000):
    def convert_optional_none_to_inner(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            args_converted = [default_value if val is None else val for val in args]
            kwargs_converted = {key: default_value if val is None else val for key, val in kwargs.items()}
            return func(*args_converted, **kwargs_converted)

        return wrapped

    return convert_optional_none_to_inner


class Message:
    MESSAGE_FORMAT = "<B2HQ2IB2I4Q"

    def __init__(self, adapter_id: int, phys_msg_type: int, time_tag: int, serial, num_data_bytes, flags, msg_sts=0x11):
        self.flags = flags
        self.num_data_bytes = num_data_bytes
        self.serial = serial
        self.time_tag = time_tag
        self.phys_msg_type = phys_msg_type
        self.adapter_id = adapter_id
        self.msg_sts = msg_sts

        self.offset_next_msg = None
        self.offset_prev_msg = None

        self.offset_next_msg_same_adapter = None
        self.offset_prev_msg_same_adapter = None

        self.offset_next_msg_type = None
        self.offset_prev_msg_type = None

    # default_pack = convert_optional_none_to(DEFAULT_VALUE)(s.pack)

    @property
    def has_all_next_fill(self) -> bool:
        return (self.offset_next_msg is not None) and\
               (self.offset_next_msg_same_adapter is not None) and \
               (self.offset_next_msg_type is not None)

    def pack(self) -> bytes:
        return s.pack(self.MESSAGE_FORMAT,
                      self.msg_sts,
                      self.adapter_id,
                      self.phys_msg_type,
                      self.time_tag,
                      self.serial,
                      self.num_data_bytes,
                      self.flags,
                      self.offset_next_msg or DEFAULT_VALUE,
                      self.offset_prev_msg or DEFAULT_VALUE,
                      self.offset_next_msg_same_adapter or DEFAULT_VALUE,
                      self.offset_prev_msg_same_adapter or DEFAULT_VALUE,
                      self.offset_next_msg_type or DEFAULT_VALUE,
                      self.offset_prev_msg_type or DEFAULT_VALUE
                      )

    def get_size(self) -> int:
        return s.calcsize(self.MESSAGE_FORMAT)


class Msg_1553(Message):
    BUS_A_XFER = 0x8000
    END_OF_MSG = 0x0100

    @convert_optional_none_to(default_value=0x0000)
    @convert_string_to_integer()
    def __init__(self,
                 cmd_word_1: int,
                 cmd_word_2: Optional[int],
                 sts_word_1: int,
                 sts_word_2: Optional[int],
                 data_words: list[str],
                 adapter_id: int,
                 phys_msg_type: int,
                 time_tag: int,
                 serial: int,
                 num_data_bytes: int,
                 flags: int,
                 flags_1553: int = 0x00,
                 msg_sts: int = 0x11,
                 px_status: int = BUS_A_XFER | END_OF_MSG):
        # make sure the child class inherit all the methods and properties from its parent
        super().__init__(adapter_id, phys_msg_type, time_tag, serial, num_data_bytes, flags, msg_sts)

        self.cmd_word_1: int = cmd_word_1
        self.cmd_word_2: int = cmd_word_2
        self.sts_word_1: int = sts_word_1
        self.sts_word_2: int = sts_word_2

        # checks for error in messages
        if data_words != 'Msg Error':
            self.data_words: list[int] = [int(data_word, BASE_HEX) for data_word in data_words]
        else:
            self.data_words: list[int] = []

        self.flags_1553 = flags_1553
        self.px_status = px_status

    @property
    def content_format(self) -> str:
        return '<5H{}HH'.format(len(self.data_words))

    def pack(self) -> bytes:
        return super().pack() + s.pack(self.content_format,
                                       self.cmd_word_1,
                                       self.cmd_word_2,
                                       self.sts_word_1,
                                       self.sts_word_2,
                                       self.px_status,
                                       *self.data_words,
                                       self.flags_1553
                                       )

    def get_size(self) -> int:
        return super().get_size() + s.calcsize(self.content_format)

    def is_write_ready(self) -> bool:
        return super().has_all_next_fill

    def write_to_output_file(self, ofstream: BinaryIO, file_position: int):
        if self.is_write_ready():
            temp_pos = ofstream.tell()

            ofstream.seek(file_position)
            ofstream.write(self.pack())

            ofstream.seek(temp_pos)
