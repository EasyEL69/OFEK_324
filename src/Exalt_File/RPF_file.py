import ijson
import pathlib
from typing import Optional, List
from dataclasses import dataclass
from src.Exalt_File.header_RPF import Header_RPF
from src.Exalt_File.sys_config import System_configuration
from src.Exalt_File.message_ex import Msg_1553
from src.Data_Structures.splay_tree import Splay_Tree
from src.Exalt_File.Markers_Tables.counts_Index_table import Counts_Index_Table
from src.Exalt_File.Markers_Tables.message_Index_table import Message_Index_Table
from src.Exalt_File.Markers_Tables.first_msg_of_type_table import First_Msg_Of_Type_Table
from src.Exalt_File.Markers_Tables.first_msg_from_adapter_table import First_Msg_From_Adapter_Table


# creating data class for type-hint the data structure
@dataclass
class elements_type_hint:
    """Class for keeping track of an item in inventory."""
    last_form_adapter: Optional[Msg_1553] = None
    splay_tree: Optional[Splay_Tree] = None


class RPF_file:
    # constants for file names
    FILE_MSGS_NAME = 'all_msgs.rpf'

    MESSAGE_INDEX_TABLE = 0
    FIRST_MSG_TYPE_TABLE = 1
    FIRST_FROM_ADAPTER_TABLE = 2
    COUNT_INDEX_TABLE = 3

    @staticmethod
    def create_exalt_msg(record: dict, table_type: int) -> Msg_1553:
        return Msg_1553(
            record['HEADER_1553']['COMMAND_WORD_1']['VALUE'],
            record['HEADER_1553']['COMMAND_WORD_2']['VALUE'],
            record['HEADER_1553']['STATUS_WORD_1'],
            record['HEADER_1553']['STATUS_WORD_2'],
            record['CONTENT_1553']['DATA_WORDS'],
            record['HEADER_CH10']['ADAPTER_ID'],
            table_type,
            record['HEADER_1553']['TIME_TAG'],
            record['HEADER_CH10']['SERIAL'],
            record['HEADER_1553']['WORD_COUNT'] * 2,
            record['HEADER_CH10']['HEADER_FLAGS']
        )

    def exalt_process(self, json_file_path: pathlib.Path, msgs_file_path: Optional[pathlib.Path] = None) -> None:

        if msgs_file_path is None:
            msgs_file_path = json_file_path.parent / self.FILE_MSGS_NAME

        with open(json_file_path, 'rb') as json_stream, open(msgs_file_path, 'wb') as msgs_ofstream:

            # in this process we will calculate the offset of the files
            # init offset
            file_offset = msgs_ofstream.tell()

            # need to remember the last msg
            last_msg_in_general: Optional[Msg_1553] = None

            # first msg of adapter list
            lst_data_streams: List[Optional[Msg_1553]] = [None] * 9

            # start iterating over the json file
            for record in ijson.items(json_stream, "item"):

                exalt_record = self.create_exalt_msg(record, self.MESSAGE_INDEX_TABLE)

                # linking between messages that sending in a chronology
                if last_msg_in_general:
                    last_msg_in_general.offset_nex_msg = exalt_record
                    exalt_record.offset_prev_msg = last_msg_in_general
                    last_msg_in_general = exalt_record

                if not self.data_stream_list_of_splay_tree[exalt_record.adapter_id].last_form_adapter:

                    # This is the first message of this adapter
                    lst_data_streams[exalt_record.adapter_id] = exalt_record

                    # this is "Last message from adapter" and creating the splay tree
                    self.data_stream_list_of_splay_tree[exalt_record.adapter_id].last_form_adapter = exalt_record
                    self.data_stream_list_of_splay_tree[exalt_record.adapter_id].splay_tree = Splay_Tree()

                else:

                    # we found the next message of this current msg from same adapter
                    self.data_stream_list_of_splay_tree[exalt_record.adapter_id] \
                        .last_form_adapter.offset_next_msg_same_adapter = exalt_record

                    # updating the previous msg link of the
                    exalt_record.offset_prev_msg_same_adapter = \
                        self.data_stream_list_of_splay_tree[exalt_record.adapter_id].last_form_adapter

                    # now after linking this is the last message from adapter
                    self.data_stream_list_of_splay_tree[exalt_record.adapter_id] \
                        .last_form_adapter = exalt_record

                    # searching for "new" command word
                    searched_node = self.data_stream_list_of_splay_tree[exalt_record.adapter_id]. \
                        splay_tree.splay(self.data_stream_list_of_splay_tree[exalt_record.adapter_id].splay_tree,
                                         key=exalt_record.cmd_word_1)

                    # if after searching we did not come across with the searched node we will insert it and splay it up
                    if not searched_node:
                        self.data_stream_list_of_splay_tree[exalt_record.adapter_id].splay_tree. \
                            insert(exalt_record, key=exalt_record.cmd_word_1)
                    else:
                        # the searched node has been founded, now we are making the links between msgs
                        self.data_stream_list_of_splay_tree[exalt_record.adapter_id].splay_tree.root. \
                            data.offset_next_msg_type = exalt_record

                        exalt_record.offset_prev_msg_type = self.data_stream_list_of_splay_tree[
                            exalt_record.adapter_id].splay_tree.root.data

                        # TODO: write root to file

                        # now we will update current data by updating the current message in root
                        # Note: when we are doing this all the fields are full
                        self.data_stream_list_of_splay_tree[exalt_record.adapter_id].splay_tree.root. \
                            data = exalt_record

    def __init__(self, num_of_msgs: int, time_tag: int, data_stream_list: list[int]):
        # creating path for rpf file
        self.rpf_path = pathlib.Path().absolute().parent.parent / 'output_files' / 'exalt_replay_file'

        # ----------------------------------------------------------------------------------------------
        # allocating splay tree for all messages for each adapter:
        # list[(last message from adapter ,adapter splay tree of msg types)] * 8 (Note:[1-8])
        self.data_stream_list_of_splay_tree: List[elements_type_hint] = \
            [elements_type_hint(last_form_adapter=None, splay_tree=None) for _ in range(9)]
        # ----------------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------------
        # creating structures for rpf file!'
        self.head_rpf: Header_RPF = Header_RPF(num_of_msgs, time_tag)
        self.sys_config: System_configuration = System_configuration(data_stream_list)

        # markers tables structures!!!
        self.first_message_from_adapter_table = First_Msg_From_Adapter_Table(time_tag, len(data_stream_list))

        # Probability of types of command words that will appear for the first time
        # in this table is about 16000 different command words
        self.first_message_from_msg_type = First_Msg_Of_Type_Table(time_tag, num_of_entries=16000)

        self.message_index_table = Message_Index_Table(time_tag, num_of_msgs)
        self.count_index_table = Counts_Index_Table(time_tag, num_of_msgs)
        # ----------------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------------
        # start main process
        self.exalt_process(pathlib.Path().absolute().parent.parent / 'resources' / 'sample.json')
        # ----------------------------------------------------------------------------------------------

    def write_bytes(self, path_to_rpf: pathlib.Path):
        with open(path_to_rpf, 'wb+') as ofstream:
            ofstream.write(self.head_rpf.to_pack())
            ofstream.write((self.sys_config.pack()))
            ofstream.write(bytes(0))  # no trigger list


def main():
    RPF_file(30, 65453121531, [1, 2, 3, 5])


if __name__ == '__main__':
    main()
