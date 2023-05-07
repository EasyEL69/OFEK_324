import json
import os
import pathlib
import sys
from tkinter import messagebox
from typing import Tuple
import ijson

try:
    from src.parsing_ch10.Py106.MsgDecode1553 import Decode1553F1
    from src.parsing_ch10.Py106.time import Time
    import src.parsing_ch10.Py106.packet as packet
    import src.parsing_ch10.Py106.status as status
    from src.parsing_ch10.message_ch10 import Message
except ImportError:
    raise ImportError


def parser_json(json_file_path: str) -> Tuple[int, list[int]]:
    num_of_msgs = 0
    adapters: list[int] = []

    try:
        with open(json_file_path, 'rb') as json_stream:
            for record in ijson.items(json_stream, "item"):
                try:
                    num_of_msgs += 1
                    add_adapter(adapters, int(record['HEADER_CH10']['ADAPTER_ID'], 16))
                except KeyError:
                    messagebox.showinfo("Process File - JSON KEYS INVALID", f"Json file is not in correct format")
                    exit(1)

    except FileNotFoundError:
        messagebox.showinfo("Process File - open file status", f"Error opening data file: {json_file_path}")
        exit(1)

    messagebox.showinfo("Process File - Finish Parser", f"done parsing json file")
    return num_of_msgs, adapters


def parser_c10(ch10_file_path: str) -> Tuple[int, list[int]]:
    """ inspired by an open src code parsing
                Created on Jan 4, 2012
                by author: rb45
            """

    json_output_file_path = pathlib.Path().absolute().parent / 'output_files' / \
                            (os.path.splitext(os.path.basename(ch10_file_path))[0] + '.json')

    # Make IRIG 106 library classes
    pkt_io = packet.IO()
    time_utils = Time(pkt_io)
    decode1553 = Decode1553F1(pkt_io)

    open_status = pkt_io.open(str(ch10_file_path), packet.FileMode.READ)

    if open_status != status.OK:
        messagebox.showinfo("Process File - open file status", f"Error opening data file: {ch10_file_path}")
        sys.exit(1)

    # file is good to go. analyzing part
    time_sync_status = time_utils.sync_time(False, 0)
    if time_sync_status != status.OK:
        messagebox.showinfo("Process File - sync file status", "Sync Status = %s" % status.Message(time_sync_status))
        sys.exit(1)

    num_msgs, adapters = parser_1553(pkt_io, decode1553, json_output_file_path)

    messagebox.showinfo("Process File - Finish Parser", f"output file in:\n{json_output_file_path}")

    return num_msgs, adapters


def add_adapter(adapters: list[int], adapter_id: int):
    if adapter_id not in adapters:
        adapters.append(adapter_id)


def parser_1553(pkt_io, decode1553, file_json_file_path) -> Tuple[int, list[int]]:
    num_of_msgs = 0
    adapters: list[int] = []

    with open(file_json_file_path, "wb+") as f:

        f.write('[\n'.encode())

        # scanning over all packets in file
        for pkt_hdr in pkt_io.packet_headers():
            # checking for 1553 data packet type
            if pkt_hdr.data_type == packet.DataType.MIL1553_FMT_1:
                # reading 1553 message data
                pkt_io.read_data()
                for msg in decode1553.msgs():
                    parsed_msg: Message = Message(pkt_hdr, msg, decode1553)
                    num_of_msgs += 1

                    add_adapter(adapters, parsed_msg.header_ch10.adapter_id)

                    chunk = json.dumps(parsed_msg.to_dict(), indent=4).encode() + ',\n'.encode()
                    f.write(chunk)
        f.seek(f.tell() - len(',\n'.encode()))
        f.write('\n]'.encode())

    return num_of_msgs, adapters


'''def main() -> None:
    parsing_process(pathlib.Path().absolute().parent.parent / 'resources' / 'sample.c10')


if __name__ == '__main__':
    main()
'''

'''def parsing_process(ch10_file_path: pathlib.Path, results_file_path: Optional[pathlib.Path] = None) -> None:
    """ inspired by an open src code parsing
                Created on Jan 4, 2012
                by author: rb45
            """
    if results_file_path is None:
        results_file_path = ch10_file_path.parent / (ch10_file_path.name.split('.', 2)[0] + '.json')

    # Make IRIG 106 library classes
    pkt_io = packet.IO()
    time_utils = Time(pkt_io)
    decode1553 = Decode1553F1(pkt_io)

    open_status = pkt_io.open(str(ch10_file_path), packet.FileMode.READ)

    if open_status != status.OK:
        messagebox.showinfo("Process File", f"Error opening data file: {ch10_file_path}")
        sys.exit(1)

    # file is good to go. analyzing part
    time_sync_status = time_utils.sync_time(False, 0)
    if time_sync_status != status.OK:
        print("Sync Status = %s" % status.Message(time_sync_status))
        sys.exit(1)

    num_msgs, adapters = parser_1553(pkt_io, decode1553, results_file_path)
'''
