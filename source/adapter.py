import struct as s


class Adapter:
    # TODO: check what the hell is the VERSION of the adapter!?!?
    ADAPTER_VERSION = 2.0

    # information will be get from outside input (input will be hush table)
    def __init__(self, hash_map, adapter_id: int):
        self._struct_bytes = s.pack(self.format_struct(hash_map, adapter_id),
                                    len(hash_map[adapter_id].name),
                                    hash_map[adapter_id].name,
                                    len(hash_map[adapter_id].mux_bus),
                                    hash_map[adapter_id].mux_bus,
                                    adapter_id,
                                    self.ADAPTER_VERSION)

    @staticmethod
    def format_struct(hash_map: any, adapter_id: int) -> str:
        """
        @param hash_map: object
        @param adapter_id: adapter serial number
        @return: bytes format string in order to pack data.
        """
        return ">I{length}sI{mux_bus_name}s2H".format(length=len(hash_map[adapter_id].name),
                                                      mux_bus_name=hash_map[adapter_id].muxbus)

    @property
    def get_bytes(self) -> bytes:
        return self._struct_bytes
