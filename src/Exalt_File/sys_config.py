import struct as s
from typing import Final

BASE_HEX: Final[int] = 16


class System_configuration:
    def __init__(self, adapters_id: list[int]):
        self.num_of_data_streams: int = len(adapters_id)
        self.list_of_data_streams: list[Adapter] = [Adapter(adapter_id) for adapter_id in adapters_id]

    def get_size(self):
        return s.calcsize('<I') + sum([data_stream.get_size() for data_stream in self.list_of_data_streams])

    def pack(self) -> bytes:
        # first we will pack the number of data streams
        packed_data: bytes = s.pack('<I', self.num_of_data_streams)

        # for each adapter in the list we will add his packed data to the buffer
        for data_stream in self.list_of_data_streams:
            packed_data += data_stream.pack()

        return packed_data


class Adapter:
    # TODO: future feature changing adapter version from config file and make a comparison with current struct to OFRI
    ADAPTER_VERSION: Final[int] = 1
    MUXBUS_NAMES: Final[list[str]] = ['amx8', 'amx5', 'amx6', 'muxd', 'amxfast', 'muxw', 'muxchoco']

    # all of adapter's type in project is MUXBUS!
    TYPE: Final[str] = 'MuxBus'

    @property
    def muxbux_name(self) -> str:
        try:
            return self.MUXBUS_NAMES[self._adapter_id - 1]
        except IndexError:
            return '______'

    def __init__(self, adapter_id: int):
        # self._adapter_id: Final[int] = int(adapter_id, BASE_HEX)
        self._adapter_id: Final[int] = adapter_id

    @property
    def format_struct(self) -> str:
        return "<i{len_name}si{len_type}s2H".format(len_name=len(self.muxbux_name),
                                                    len_type=len(self.TYPE))

    def get_size(self) -> int:
        return s.calcsize(self.format_struct)

    def pack(self) -> bytes:
        # Note: when using string buffer for packing make sure to encode the string before packing it with
        # encode/bytes function
        return s.pack(self.format_struct,
                      len(self.muxbux_name),
                      self.muxbux_name.encode('utf-8'),
                      len(self.TYPE),
                      self.TYPE.encode('utf-8'),
                      self._adapter_id,
                      self.ADAPTER_VERSION)
