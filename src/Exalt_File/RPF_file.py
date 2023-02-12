from typing import Optional
from src.Exalt_File.header_RPF import Header_RPF
from src.Exalt_File.sys_config import System_configuration
from src.Exalt_File.Markers_Tables.counts_Index_table import Counts_Index_Table
from src.Exalt_File.Markers_Tables.message_Index_table import First_Msg_Of_Type_Table
from src.Exalt_File.Markers_Tables.first_msg_of_type_table import First_Msg_Of_Type_Table
from src.Exalt_File.Markers_Tables.first_msg_from_adapter_table import First_Msg_From_Adapter_Table
from src.Data_Structures.splay_tree import SplayTree


class RPF_file:
    def __init__(self, num_of_msgs: int, time_tag: int, data_stream_list: list[int]):
        msgs_tree: Optional[SplayTree] = None
        self.head_rpf: Header_RPF = Header_RPF(num_of_msgs, time_tag)
        self.sys_config: System_configuration = System_configuration(data_stream_list)

    def write_bytes(self, path_to_rpf: str):
        with open(path_to_rpf, 'wb+') as ofstream:
            ofstream.write(self.head_rpf.to_pack())
            ofstream.write((self.sys_config.pack()))
            ofstream.write(0)  # no trigger list
