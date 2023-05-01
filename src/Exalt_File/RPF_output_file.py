import pathlib
import struct
import sys
from dataclasses import dataclass
from queue import Queue
from tkinter import messagebox
from typing import Tuple, Optional, List, BinaryIO, Union, Final

import ijson

from src.Data_Structures.splaytree import SplayTree, Node, Node_data_elements
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

# File pointers and position constants
# --------------------------------------
FILE_START_POSITION = 0
NO_TRIGGER_LIST = NO_GAP_LIST = NO_MARK_LIST = NO_POINTER = 0
# --------------------------------------

# Marker tables index list
# --------------------------------------
MESSAGE_INDEX_TABLE = 0
FIRST_MSG_TYPE_TABLE = 1
FIRST_FROM_ADAPTER_TABLE = 2
COUNT_INDEX_TABLE = 3
# --------------------------------------

# Trigger list size is known in bytes
# --------------------------------------
TRIGGER_LIST_SIZE = struct.calcsize("<i")
# --------------------------------------

# Set queue buffer max size for writing and holding messages
# --------------------------------------
QUEUE_MAX_SIZE = 150
# --------------------------------------


# Creating data class for type-hint the data structure
# --------------------------------------------------------------------------
@dataclass
class LastMsg:
    message: Optional[Msg_1553] = None
    file_position: Optional[int] = None


@dataclass
class AdaptersElement:
    message: Optional[Msg_1553] = None
    file_position: Optional[int] = None


@dataclass
class QueueItem:
    msg_1553: Optional[Msg_1553] = None
    file_position: Optional[int] = None


# --------------------------------------------------------------------------


# Additional function for creating file objects set their values
# --------------------------------------------------------------------------
def calculate_offset(current: int, last_position: int) -> int:
    return abs(current - last_position)


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


# --------------------------------------------------------------------------


# Additional function that using data structures
# --------------------------------------------------------------------------
def send_queue_to_rpf(ofstream: BinaryIO, queue_buffer: Queue[Optional[QueueItem]]) -> None:
    """
    @param ofstream: output_file pointer in order to fill 1553 messages to RPF file
    @param queue_buffer: queue of 1553 messages to be writen to an output file
    @return: None
    @note: function will write all messages in queue that can be written to file.
           notice file position won't change at the end of the function
    """

    # saving last position of file pointer to seek back to
    saved_position: int = ofstream.tell()

    # init flag element for checking if queue make a circle
    flag_item = None

    # while queue is not empty and queue doesn't do circle
    while not queue_buffer.empty() and flag_item is not queue_buffer.queue[0]:

        # extract top of queue
        item: QueueItem = queue_buffer.get()

        # check if we can write message to file (when all next file offset has been filled)
        if item.msg_1553.is_write_ready():
            # when file pointer is the same as message file position => we write continuously no file seek is require
            if item.file_position != ofstream.tell():
                ofstream.seek(item.file_position)
            ofstream.write(item.msg_1553.pack())
        else:
            # check if it is the first message we want track the queue circle
            if flag_item is None:
                flag_item = item
            # message that we didn't write to file return to queue
            queue_buffer.put(item)

    # returning to last file pointer position before function
    ofstream.seek(saved_position)


def insert_msg_to_queue(ofstream: BinaryIO, queue_buffer: Queue[Optional[QueueItem]],
                        current_msg: Optional[Msg_1553], current_position: int) -> None:
    """
    @param ofstream: output_file pointer in order to fill 1553 messages to RPF file
    @param queue_buffer: queue of 1553 messages to be writen to an output file
    @param current_msg: current 1553 message system read
    @param current_position: current file position
    @return: None
    @note: function will dequeue messages as many as it can, and check for queue overflow
           then it makes a decision to insert message to queue
    """

    # When queue is full we will write 1553 messages that is ready to be written
    # as many as we can to provide more space in queue
    if queue_buffer.full():
        send_queue_to_rpf(ofstream, queue_buffer)

    # if queue is still full system cannot handel the massive data
    # file cannot be converted to rpf, then exist from system
    if queue_buffer.full():
        messagebox.showinfo("Process File - FATAL ERROR SYSTEM", 'Queue Overflow')
        sys.exit(1)

    # there is a place to insert message in messages queue buffer
    queue_buffer.put(QueueItem(msg_1553=current_msg, file_position=current_position))


def fill_no_pointer_value(root: Optional[Node]) -> None:
    """
    @param root: root of messages type splay tree
    @return: None
    @note: function fill message next type file pointer to NO_POINTER value
    """
    # when root is none we finished scanning over tree
    if root is None:
        return

    # set root data next message type pointer to be NO_POINTER value
    root.data.data_1553.offset_next_msg_type = NO_POINTER

    # same task on left and right subtrees
    fill_no_pointer_value(root.left)
    fill_no_pointer_value(root.right)


# --------------------------------------------------------------------------


# Additional function to RPF algorithm handling
# --------------------------------------------------------------------------
def handling_last_message(last_msg: LastMsg, current_msg: Optional[Msg_1553], current_position: int) -> None:
    """
    @param last_msg: last 1553 message system has read before
    @param current_msg: current 1553 message system read
    @param current_position: current file position
    @return: None
    @note: function will update last data param to keep tracking the order
    """

    # check if message exist before current message
    if last_msg.message:

        # linking last message to current message and update the last message
        last_msg.message.offset_next_msg = current_msg.offset_prev_msg = \
            calculate_offset(current_position, last_msg.file_position)

    else:
        # first message that system get, previous message does not exist
        current_msg.offset_prev_msg = NO_POINTER

    # update the current message to be the last one that we get
    last_msg.message = current_msg
    last_msg.file_position = current_position


def handling_last_from_adapter_message(last_from_adapters: List[AdaptersElement],
                                       current_msg: Optional[Msg_1553],
                                       current_position: int,
                                       first_form_adapter_table: First_Msg_From_Adapter_Table) -> None:
    """
    @param last_from_adapters: list of maximum adapters that can be in input file, contains 1553 msg and file position
    @param current_msg: current 1553 message system read from input file
    @param current_position: current file position
    @param first_form_adapter_table: marker table that contains all first messages from adapter entries
    @return: None
    @note: function will update file pointers between two messages, message from last adapter and current message
           also, update marker table entries
    """
    # extract current adapter list index
    adapter_id: Final[int] = current_msg.adapter_id

    # check if this message is the first from any adapter in the list
    if not last_from_adapters[adapter_id].message:

        # ---- YES! first message from adapter --------
        # we will add this file position to the first message from adapter table
        first_form_adapter_table.add_entry(First_Message_From_Adapter_Entry(current_position, adapter_id))

        # first message from this adapter that system get, previous message does not exist
        current_msg.offset_prev_msg_same_adapter = NO_POINTER

    else:
        # we have a last message from this adapter
        # we are going to link it to current message
        last_from_adapters[adapter_id].message.offset_next_msg_same_adapter = \
            current_msg.offset_prev_msg_same_adapter = \
            calculate_offset(current_position, last_from_adapters[adapter_id].file_position)

    # update the last message from this adapter and his file position
    last_from_adapters[current_msg.adapter_id].message = current_msg
    last_from_adapters[current_msg.adapter_id].file_position = current_position


def handling_file_message_type(msgs_type_splay_tree: SplayTree, current_msg: Optional[Msg_1553],
                               current_position: int, first_message_type_table: First_Msg_Of_Type_Table) -> None:
    """
    @param msgs_type_splay_tree: a splay tree of all message type we get from input file
    @param current_msg: current 1553 message system read from input file
    @param current_position: current file position
    @param first_message_type_table: marker table that contains all first messages from message type entries
    @return: None
    @note: function will update file pointers between two messages with same type,
           message from last adapter and current message.
           Also, update marker table entries and update the message type splay tree
    """

    # splay the type of the message we came across with (if type does not exist func will return None)
    splayed_node = msgs_type_splay_tree.splay(root=msgs_type_splay_tree.root, key=current_msg.cmd_word_1)

    # if Message Type is not in tree meaning it is the first message from message type
    if not splayed_node:

        # adding type to table
        first_message_type_table.add_entry(First_Message_Of_Type_Entry(current_position, current_msg.cmd_word_1))

        # insert message to tree
        msgs_type_splay_tree.insert(Node_data_elements(data_1553=current_msg,
                                                       file_position=current_position),
                                    key=current_msg.cmd_word_1)

        # first message type that system get, previous message does not exist
        current_msg.offset_prev_msg_type = NO_POINTER

    # message type is already in tree, then it splayed up, and now we will extract the data and packing it
    else:
        root_node_data: Node_data_elements = msgs_type_splay_tree.root.data
        msgs_type_splay_tree.root.data = Node_data_elements(data_1553=current_msg, file_position=current_position)

        # linking offset between 2 messages
        calculated_offset = calculate_offset(current_position, root_node_data.file_position)
        root_node_data.data_1553.offset_next_msg_type = calculated_offset
        msgs_type_splay_tree.root.data.data_1553.offset_prev_msg_type = calculated_offset


def fill_rest_file_pointers(last_msg: LastMsg, last_from_adapters: List[AdaptersElement],
                            msgs_type_splay_tree: SplayTree) -> None:
    """
    @param last_msg: last 1553 message system get
    @param last_from_adapters: list of maximum adapters that can be in input file, contains 1553 msg and file position
    @param msgs_type_splay_tree: a splay tree of all message type we get from input file
    @return: None
    @note: function will set all kinds of next file pointers to be NO_POINTER value
    """

    # fill last message next pointer to NO_POINTER value because there isn't next message
    last_msg.message.offset_next_msg = NO_POINTER

    # fill all last message from adapter next pointer to NO_POINTER value because there isn't next message
    for last_adapter in last_from_adapters:
        if last_adapter.message is not None:
            last_adapter.message.offset_next_msg_same_adapter = NO_POINTER

    # fill rest of messages in type splay tree with NO_POINTER value because there isn't next message
    fill_no_pointer_value(root=msgs_type_splay_tree.root)


# --------------------------------------------------------------------------


# main creating file output rpf file process
def rpf_algorithm(json_stream: BinaryIO, ofstream: BinaryIO, marker_table_list, max_eval_num_adapters: int) -> None:
    """
    @param json_stream: input file pointer in order to read 1553 messages
    @param ofstream: output_file pointer in order to fill 1553 messages to RPF file
    @param marker_table_list: list of all marker tables that contained in file
    @param max_eval_num_adapters: the highest adapter ID in adapters list
    @return: None
    @note:  function fill all 1553 messages in RPF file!
    """
    # list of the marker tables with filled data
    # -----------------------------------------------------------------

    # Remember what is the last msg system got
    last_msg: LastMsg = LastMsg(message=None, file_position=None)

    # Remember all last messages from all the adapters
    last_from_adapters: List[AdaptersElement] = \
        [AdaptersElement(message=None, file_position=None) for _ in
         range(max_eval_num_adapters + 1)]

    # Init splay tree for managing type message searching and type message inserting
    # to provide less time complexity
    msgs_type_splay_tree: SplayTree = SplayTree()

    # Init queue buffer for writing chunks of 1553 data in order
    # to prevent large file seeks as many as we can
    msgs_queue_to_write: Queue[Optional[QueueItem]] = Queue(QUEUE_MAX_SIZE)
    # -----------------------------------------------------------------

    # start iterating over the json file
    for record in ijson.items(json_stream, "item"):
        # --------------------------------------------------------------------------------------
        # save current message file position and making its file object
        cur_position = ofstream.tell()
        exalt_record: Msg_1553 = create_exalt_msg(record)

        # insert message to queue
        insert_msg_to_queue(ofstream, msgs_queue_to_write, exalt_record, cur_position)

        # allocate padding for current message in file
        ofstream.seek(exalt_record.get_size(), 1)
        # --------------------------------------------------------------------------------------

        # Last message part
        # --------------------------------------------------------------------------------------
        handling_last_message(last_msg, exalt_record, cur_position)
        # ----------------------------------------------------------------------------------------

        # ADAPTER PART ------------------------------------------------------------------------------------------
        handling_last_from_adapter_message(last_from_adapters,
                                           exalt_record,
                                           cur_position,
                                           marker_table_list[FIRST_FROM_ADAPTER_TABLE])
        # END ADAPTER PART --------------------------------------------------------------------------------------

        # MSG TYPE PART ------------------------------------------------------------------------------------------
        handling_file_message_type(msgs_type_splay_tree,
                                   exalt_record,
                                   cur_position,
                                   marker_table_list[FIRST_MSG_TYPE_TABLE])
        # END MSG TYPE PART --------------------------------------------------------------------------------------

    # fill rest file pointers
    fill_rest_file_pointers(last_msg, last_from_adapters, msgs_type_splay_tree)

    # write rest of messages in queue to file
    send_queue_to_rpf(ofstream, msgs_queue_to_write)


def write_footer(output_stream: BinaryIO) -> Tuple[int, int]:
    gap_list_pos = output_stream.tell()
    output_stream.write(struct.pack("<I", NO_GAP_LIST))

    mark_list_pos = output_stream.tell()
    output_stream.write(struct.pack("<I", NO_MARK_LIST))

    return gap_list_pos, mark_list_pos


def rpf_process(json_path, file_name: str, num_of_msgs: int, data_stream_list: list[int], time_tag: int) -> None:
    """
    @param json_path: json file input path in order to read 1553 messages
    @param file_name: the name of the RPF file
    @param num_of_msgs: the number of 1553 messages in input file
    @param data_stream_list: list of adapters id's
    @param time_tag: current time tag of the created RPF file
    @return: None
    @note: function will produce RPF as output in Output_files directory
    """

    # setting the output path in correct directory
    rpf_path = pathlib.Path().absolute().parent / 'output_files' / f'{file_name}.rpf'

    # ----------------------------------------------------------------------------------------------
    # Open output file and input file and get their file pointers
    # ----------------------------------------------------------------------------------------------

    with open(rpf_path, 'wb') as output_stream, open(json_path, 'rb') as input_stream:
        # Creating all header objects file
        # ---------------------------------------------------------------------------------------
        header_output_file: Header_RPF = Header_RPF(num_of_msgs, time_tag)
        lst_adapters_in_system: System_configuration = System_configuration(data_stream_list)
        marker_tables: List[Union[Message_Index_Table,
                                  First_Msg_Of_Type_Table,
                                  First_Msg_From_Adapter_Table,
                                  Counts_Index_Table]] = \
            list(init_tables(time_tag, len(data_stream_list)))

        # ---------------------------------------------------------------------------------------

        # First we will write all 1553 messages. then, we will write all content to file
        # ---------------------------------------------------------------------------------------
        bytes_to_seek = header_output_file.get_size() + \
                        lst_adapters_in_system.get_size() + \
                        TRIGGER_LIST_SIZE + \
                        sum([marker_table.get_size() for marker_table in marker_tables])

        # For padding in file, then we will fill the empty place
        output_stream.seek(bytes_to_seek, 1)

        # ---------------------------------------------------------------------------------------

        # RPF main algorithm to fill file properly
        # ---------------------------------------------------------------------------------------
        rpf_algorithm(input_stream, output_stream, marker_tables, max(data_stream_list))
        # ---------------------------------------------------------------------------------------

        # After finishing filling all messages we can set and write the gap list position and mark list position and
        # ---------------------------------------------------------------------------------------
        gap_list_pos, mark_list_pos = write_footer(output_stream)
        # ---------------------------------------------------------------------------------------

        # Now we can fill the header objects to file.
        # ---------------------------------------------------------------------------------------
        # seeking to file start position
        output_stream.seek(FILE_START_POSITION)

        # setting what is the gap and mark lists positions
        header_output_file.set_gap_list_pos(gap_list_pos)
        header_output_file.set_mark_list_pos(mark_list_pos)

        # write packed data to file
        output_stream.write(header_output_file.to_pack())
        output_stream.write(lst_adapters_in_system.pack())
        output_stream.write(struct.pack("<i", NO_TRIGGER_LIST))
        for marker_table in marker_tables:
            output_stream.write(marker_table.pack())

        # letting user know process ends correctly
        messagebox.showinfo("Process File - Done :)", f"File path:\n {rpf_path}")

        # ---------------------------------------------------------------------------------------
