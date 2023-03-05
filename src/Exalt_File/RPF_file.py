import ijson
import pathlib
import random
from typing import Optional
from src.Exalt_File.header_RPF import Header_RPF
from src.Exalt_File.sys_config import System_configuration
from src.Exalt_File.message_ex import Msg_1553
from src.Exalt_File.Markers_Tables.counts_Index_table import Counts_Index_Table
from src.Exalt_File.Markers_Tables.message_Index_table import First_Msg_Of_Type_Table
from src.Exalt_File.Markers_Tables.first_msg_of_type_table import First_Msg_Of_Type_Table
from src.Exalt_File.Markers_Tables.first_msg_from_adapter_table import First_Msg_From_Adapter_Table


class RPF_file:
    FILE_MSGS_NAME = 'all_msgs.rpf'

    @staticmethod
    def create_exalt_msg(record: dict) -> Msg_1553:
        return Msg_1553(
            record['HEADER_1553']['COMMAND_WORD_1']['VALUE'],
            record['HEADER_1553']['COMMAND_WORD_2']['VALUE'],
            record['HEADER_1553']['STATUS_WORD_1'],
            record['HEADER_1553']['STATUS_WORD_2'],
            record['CONTENT_1553']['DATA_WORDS'],
            record['HEADER_CH10']['ADAPTER_ID'],
            random.randint(0, 3),  # physical message type
            record['HEADER_1553']['TIME_TAG'],
            record['HEADER_CH10']['SERIAL'],
            record['HEADER_1553']['WORD_COUNT'] * 2,
            record['HEADER_CH10']['HEADER_FLAGS']
        )

    def write_all_msgs(self, json_file_path: pathlib.Path, msgs_file_path: Optional[pathlib.Path] = None) -> None:

        if msgs_file_path is None:
            msgs_file_path = json_file_path.parent / self.FILE_MSGS_NAME

        with open(json_file_path, 'rb') as json_stream, open(msgs_file_path, 'wb') as mgs_ofstream:
            for record in ijson.items(json_stream, "item"):
                exalt = self.create_exalt_msg(record)
                exalt.pack()

    def __init__(self, num_of_msgs: int, time_tag: int, data_stream_list: list[int]):
        self.head_rpf: Header_RPF = Header_RPF(num_of_msgs, time_tag)
        self.sys_config: System_configuration = System_configuration(data_stream_list)

        self.write_all_msgs(pathlib.Path().absolute().parent.parent / 'resources' / 'sample.json')

    def write_bytes(self, path_to_rpf: pathlib.Path):
        with open(path_to_rpf, 'wb+') as ofstream:
            ofstream.write(self.head_rpf.to_pack())
            ofstream.write((self.sys_config.pack()))
            ofstream.write(0)  # no trigger list

            # TODO: write the markers tables!
            # TODO: write all messages


def main():
    RPF_file(30, 65453121531, [1, 2, 3, 5])


if __name__ == '__main__':
    main()
