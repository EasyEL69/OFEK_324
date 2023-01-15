import struct as s
from typing import Final
import source.constants as c


class Adapter:
    # TODO: future feature changing adapter version from config file
    ADAPTER_VERSION = 1
    MUXBUS_NAMES = ['amx8', 'amx5', 'amx6', 'muxd', 'amxfast', 'muxw', 'muxchoco']

    # all of adapter's type in project is MUXBUS!
    TYPE = 'MuxBus'
    TYPE_LEN = 6

    @property
    def muxbux_name(self) -> str:
        try:
            return self.MUXBUS_NAMES[self._adapter_id - 1]
        except IndexError:
            return 'muxbus not found'

    def __init__(self, adapter_id: str):
        self._adapter_id: Final[int] = int(adapter_id, c.BASE_HEX)

    @property
    def format_struct(self) -> str:
        return ">i{len_name}si{len_type}s2H".format(len_name=len(self.muxbux_name),
                                                    len_type=self.TYPE_LEN)

    def to_pack(self) -> bytes:
        # Note: when using string buffer for packing make sure to encode the string before packing it with
        # encode/bytes function
        return s.pack(self.format_struct,
                      len(self.muxbux_name),
                      self.muxbux_name.encode('utf-8'),
                      self.TYPE_LEN,
                      self.TYPE.encode('utf-8'),
                      self._adapter_id,
                      self.ADAPTER_VERSION)
