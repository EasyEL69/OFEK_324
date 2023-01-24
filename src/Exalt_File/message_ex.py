import struct as s
from abc import ABC
from typing import Optional
import functools


class Message(ABC):
    MESSAGE_FORMAT = ">B2HQ2IB2I4Q"

    num_of_msg = 0

    def __init__(self, msg_sts, adapter_id, phys_msg_type, time_tag, serial, num_data_bytes, flags):
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

    # TODO: check with Yitzhak that offset is written correctly in big indian
    def pack(self) -> bytes:
        return s.pack(self.MESSAGE_FORMAT,
                      self.msg_sts,
                      self.adapter_id,
                      self.phys_msg_type,
                      self.time_tag,
                      self.num_data_bytes,
                      self.flags,
                      self.offset_next_msg,
                      self.offset_prev_msg,
                      self.offset_next_msg_same_adapter,
                      self.offset_prev_msg_same_adapter,
                      self.offset_next_msg_type,
                      self.offset_prev_msg_type
                      )

    # TODO: set implement to set_offset func when algorithm is implement

    def set_offset_to_next_msg(self, offset: int) -> None:
        self.offset_next_msg = offset

    def set_offset_to_prev_msg(self, offset: int) -> None:
        self.offset_prev_msg = offset

    def set_offset_next_msg_same_adapter(self, offset: int) -> None:
        self.offset_next_msg_same_adapter = offset

    def set_offset_prev_msg_same_adapter(self, offset: int) -> None:
        self.offset_prev_msg_same_adapter = offset

    def set_offset_next_msg_type(self, offset: int) -> None:
        self.offset_next_msg_type = offset

    def set_offset_prev_msg_type(self, offset: int) -> None:
        self.offset_prev_msg_type = offset

    @classmethod
    def inc_num_of_msg(cls):
        cls.num_of_msg += 1

    @classmethod
    def get_num_of_msgs(cls):
        return cls.num_of_msg


def convert_optional_none_to(default_value=0x0000):
    def convert_optional_none_to_inner(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            args_converted = [default_value if val is None else val for val in args]
            kwargs_converted = {key: default_value if val is None else val for key, val in kwargs.items()}
            return func(*args_converted, **kwargs_converted)

        return wrapped

    return convert_optional_none_to_inner


class Msg_1553(Message):
    BUS_A_XFER = 0x8000
    END_OF_MSG = 0x0100

    @convert_optional_none_to(default_value=0x0000)
    def __init__(self,
                 cmd_word_1: int,
                 cmd_word_2: Optional[int],
                 sts_word_1: int,
                 sts_word_2: Optional[int],
                 data_words: list[int],
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
        super().__init__(msg_sts, adapter_id, phys_msg_type, time_tag, serial, num_data_bytes, flags)

        self.cmd_word_1 = cmd_word_1
        self.cmd_word_2 = cmd_word_2
        self.sts_word_1 = sts_word_1
        self.sts_word_2 = sts_word_2
        self.data_words = data_words
        self.flags_1553 = flags_1553
        self.px_status = px_status

    @property
    def content_format(self) -> str:
        return '>5H{}HH'.format(len(self.data_words))

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
