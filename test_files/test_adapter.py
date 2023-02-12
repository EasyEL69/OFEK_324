from src.Exalt_File.sys_config import Adapter
import struct as s


def test_creating_methode():
    test_adapter = Adapter('0005')

    # make sure object is created
    assert test_adapter is not None

    # adapter is in range!
    assert test_adapter.muxbux_name != 'muxbus not found'

    # name muxbus should be amxfast
    assert test_adapter.format_struct == '>i7si6s2H'

    assert test_adapter.muxbux_name == 'amxfast'


def test_not_existing_adapter():
    test_adapter = Adapter('00400')

    # make sure object is created
    assert test_adapter is not None

    # adapter is in range!
    assert test_adapter.muxbux_name == 'muxbus not found'

    # name muxbus should be amx6
    assert test_adapter.format_struct == '>i16si6s2H'

    assert test_adapter.muxbux_name != 'muxchoco'


def packing_bytes():
    # muxbus: "muxw"
    test_adapter = Adapter('0006')

    # make sure they have the same size bytes
    assert s.calcsize('i4si6s2H') == s.calcsize(test_adapter.format_struct)

    test_bytes: bytes = test_adapter.to_pack()

    # now we will unpack the bytes and see if we will get the same values.
    values = s.unpack(test_adapter.format_struct, test_bytes)
    print(values)


packing_bytes()
