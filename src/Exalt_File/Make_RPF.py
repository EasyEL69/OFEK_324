import pathlib
import struct
from dataclasses import dataclass
from typing import Tuple, Optional, List, BinaryIO

import ijson

from src.Data_Structures.splaytree import SplayTree, Node_data_elements
from src.Exalt_File.Markers_Tables.Entries.first_message_from_adapter_entry import First_Message_From_Adapter_Entry
from src.Exalt_File.Markers_Tables.Entries.first_message_of_type_entry import First_Message_Of_Type_Entry
from src.Exalt_File.Markers_Tables.counts_Index_table import Counts_Index_Table
from src.Exalt_File.Markers_Tables.first_msg_from_adapter_table import First_Msg_From_Adapter_Table
from src.Exalt_File.Markers_Tables.first_msg_of_type_table import First_Msg_Of_Type_Table
from src.Exalt_File.Markers_Tables.message_Index_table import Message_Index_Table
from src.Exalt_File.header_RPF import Header_RPF
from src.Exalt_File.message_ex import Msg_1553
from src.Exalt_File.sys_config import System_configuration

# Constants for algorithm

NO_TRIGGER_LIST = 0
# --------------------------------------
MESSAGE_INDEX_TABLE = 0
FIRST_MSG_TYPE_TABLE = 1
FIRST_FROM_ADAPTER_TABLE = 2
COUNT_INDEX_TABLE = 3
# --------------------------------------

# --------------------------------------
MESSAGE_1553 = 0
FILE_POSITION = 1


# --------------------------------------


# creating data class for type-hint the data structure
@dataclass
class last_msg_general_elements_type_hint:
    """Class for keeping track of an item in inventory."""
    last_msg: Optional[Msg_1553] = None
    last_msg_pos: Optional[int] = None


@dataclass
class adapters_elements_type_hint:
    """Class for keeping track of an item in inventory."""
    last_form_adapter: Optional[Msg_1553] = None
    last_form_adapter_pos: Optional[int] = None


def calculate_offset(current: int, last_position: int) -> int:
    return current - last_position


def create_exalt_msg(record: dict) -> Msg_1553:
    return Msg_1553(
        record['HEADER_1553']['COMMAND_WORD_1']['VALUE'],  # first command word
        record['HEADER_1553']['COMMAND_WORD_2']['VALUE'],  # second command word (maybe doesn't exist in message)
        record['HEADER_1553']['STATUS_WORD_1'],  # first status word (exist!)
        record['HEADER_1553']['STATUS_WORD_2'],  # second status word (maybe doesn't exist in message)
        record['CONTENT_1553']['DATA_WORDS'],  # all data words in message
        record['HEADER_CH10']['ADAPTER_ID'],  # adapter id
        record['HEADER_1553']['COMMAND_WORD_1']['VALUE'],  # The msg_type is also the command word
        record['HEADER_1553']['TIME_TAG'],  # Time Tag of a message
        record['HEADER_CH10']['SERIAL'],  # serial number of a message
        record['HEADER_1553']['WORD_COUNT'] * 2,  # num of byte were getting according to command word
        record['HEADER_CH10']['HEADER_FLAGS']  # header message flags we get in header package
    )


def init_tables(time_tag: int, num_adapters: int) -> \
        Tuple[Message_Index_Table, First_Msg_Of_Type_Table, First_Msg_From_Adapter_Table, Counts_Index_Table]:
    return \
        Message_Index_Table(time_tag), \
        First_Msg_Of_Type_Table(time_tag, 2 ^ 16), \
        First_Msg_From_Adapter_Table(time_tag, num_adapters), \
        Counts_Index_Table(time_tag)


def file_tables_rpf(input_path: pathlib.Path, time_tag: int, num_of_adapters: int, ofstream: BinaryIO) -> None:
    tables = list(init_tables(time_tag, num_of_adapters))
    num_of_bytes = sum([table.get_size() for table in tables])

    # after finishing filling the tables we will pack it with the data
    tables_pointer = ofstream.tell()

    # for padding in file
    ofstream.write(struct.pack(f"{num_of_bytes}x"))


def rpf_algorithm(json_stream: BinaryIO, ofstream: BinaryIO, table_list, max_eval_num_adapters: int):
    # -----------------------------------------------------------------
    # need to remember the last msg
    last_msg_in_general: last_msg_general_elements_type_hint = \
        last_msg_general_elements_type_hint(last_msg=None, last_msg_pos=None)

    last_from_adapters: List[adapters_elements_type_hint] = \
        [adapters_elements_type_hint(last_form_adapter=None, last_form_adapter_pos=None) for _ in
         range(max_eval_num_adapters)]

    # init splay tree for algorithm
    msgs_type_splay_tree: SplayTree = SplayTree()
    # -----------------------------------------------------------------

    # start iterating over the json file
    for record in ijson.items(json_stream, "item"):

        cur_position = ofstream.tell()
        exalt_record: Msg_1553 = create_exalt_msg(record)

        # allocate padding for current message in file
        ofstream.write(struct.pack(f"{exalt_record.get_size()}x"))

        # --------------------------------------------------------------------------------------
        # linking last message to current message and update the last message
        if last_msg_in_general.last_msg:
            # there is a message before current message then we can link between them

            last_msg_in_general.last_msg.offset_nex_msg = exalt_record.offset_prev_msg = \
                calculate_offset(cur_position, last_msg_in_general.last_msg_pos)

        if last_msg_in_general.last_msg.is_write_ready():
            temp_pos = ofstream.tell()
            ofstream.seek(last_msg_in_general.last_msg_pos)
            ofstream.write(last_msg_in_general.last_msg.pack())
            ofstream.seek(temp_pos)

        # update the current message to be the last one that we get
        last_msg_in_general.last_msg = exalt_record
        last_msg_in_general.last_msg_pos = cur_position

        # ----------------------------------------------------------------------------------------

        # ADAPTER PART ------------------------------------------------------------------------------------------
        # check if this msg is the first from adapter
        if not last_from_adapters[exalt_record.adapter_id].last_form_adapter:

            # ---- YES! first message from adapter --------
            tables[FIRST_FROM_ADAPTER_TABLE]. \
                add_entry(First_Message_From_Adapter_Entry(cur_position, exalt_record.adapter_id))

            # now that not the first message from adapter
            last_from_adapters[exalt_record.adapter_id].last_form_adapter = exalt_record
            last_from_adapters[exalt_record.adapter_id].last_form_adapter_pos = cur_position

        else:
            # we have a message from this adapter, we are going to link it
            last_from_adapters[exalt_record.adapter_id].last_form_adapter. \
                offset_next_msg_same_adapter = exalt_record.offset_prev_msg_same_adapter = \
                calculate_offset(cur_position, last_from_adapters[exalt_record.adapter_id].last_form_adapter_pos)

            if last_from_adapters[exalt_record.adapter_id].last_form_adapter.is_write_ready():
                ofstream.write(last_from_adapters[exalt_record.adapter_id].last_form_adapter.pack())

            last_from_adapters[exalt_record.adapter_id].last_form_adapter = exalt_record
            last_from_adapters[exalt_record.adapter_id].last_form_adapter_pos = cur_position

        # END ADAPTER PART --------------------------------------------------------------------------------------

        # MSG TYPE PART ------------------------------------------------------------------------------------------
        # splay the type of the message we came across with (if type does not exist func will return None)
        splayed_node = msgs_type_splay_tree.splay(root=msgs_type_splay_tree.root, key=exalt_record.cmd_word_1)

        # if Message Type is not in tree meaning it is the first message from message type
        if not splayed_node:

            # adding type to table
            tables[FIRST_MSG_TYPE_TABLE]. \
                add_entry(First_Message_Of_Type_Entry(cur_position, exalt_record.cmd_word_1))

            # insert message to tree
            msgs_type_splay_tree.insert(Node_data_elements(data_1553=exalt_record, file_position=cur_position),
                                        key=exalt_record.cmd_word_1)

        # message type is already in tree, then it splayed up, and now we will extract the data and packing it
        else:
            last_msg_type_node_data: Node_data_elements = msgs_type_splay_tree.root.data
            msgs_type_splay_tree.root.data = Node_data_elements(data_1553=exalt_record, file_position=cur_position)

            # linking offset between 2 messages

            last_msg_type_node_data.data_1553.offset_next_msg_type = \
                msgs_type_splay_tree.root.data.data_1553.offset_prev_msg_type = \
                calculate_offset(cur_position, last_msg_type_node_data.file_position)

            if last_msg_type_node_data.data_1553.is_write_ready():
                ofstream.write(last_msg_in_general.last_msg.pack())

    # write the rest messages

    # END MSG TYPE PART --------------------------------------------------------------------------------------


def rpf_process(json_path, file_name: str, num_of_msgs: int, data_stream_list: list[int], time_tag: int) -> None:
    rpf_path = pathlib.Path().absolute().parent / 'output_files' / f'{file_name}.rpf'

    # ----------------------------------------------------------------------------------------------
    # start running over packing all data
    # ----------------------------------------------------------------------------------------------

    with open(rpf_path, 'wb') as output_file:
        # TODO: change Header_rpf packing
        # we will save pointer for the header file to change gap and mark list position
        pointer = output_file.tell()

        output_file.write(Header_RPF(num_of_msgs, time_tag).to_pack())
        output_file.write(System_configuration(data_stream_list).pack())

        # NO Trigger list
        output_file.write(struct.pack("<I", NO_TRIGGER_LIST))

    # ----------------------------------------------------------------------------------------------


def main():
    print(pathlib.Path().absolute().parent.parent / 'resources' / 'sample.json')


if __name__ == '__main__':
    main()
