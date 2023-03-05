import io
from typing import Union, Tuple, Optional
from src.Data_Structures.splay_tree import Splay_Tree
from src.Exalt_File.message_ex import Msg_1553
import ijson


class Messages_file:
    def __init__(self):
        with open('C:/Users/user/Documents/GitHub/Ofek_Master_Proj/OFEK_324/resources/sample.json', 'r') as f:
            self.file_algorithm(f, f, 32, 8)

    @staticmethod
    def file_algorithm(i_fname: io.TextIOWrapper, o_fname: io.TextIOWrapper,
                       msgs_counter: Union[int, float], num_of_adapters: int):

        # init array for last msgs from adapter
        adapters: list[Tuple[Optional[Splay_Tree], Optional[Msg_1553]]] = [(None, None)] * num_of_adapters

        # in each splay tree for SAME adapter we will save all msgs form same type?

        records = ijson.items(i_fname, 'item')
        for record in records:
            # Do something with the object
            print()


def main():
    Messages_file()


if __name__ == '__main__':
    main()
