from src.Exalt_File.Markers_Tables.Entries.message_index_entry import Message_Index_Entry
from src.Exalt_File.Markers_Tables.Entries.entry import Entry
from src.Exalt_File.Markers_Tables.message_Index_table import First_Msg_Of_Type_Table


def tester_func_1():
    num_of_entries = 8
    entries = [Entry()] * num_of_entries
    for i in range(len(entries)):
        entries[i] = Message_Index_Entry()

    print(entries)
    print('I love u')


def tester_func_2():
    table: First_Msg_Of_Type_Table = First_Msg_Of_Type_Table(num_of_entries=8)
    print(table.pack())


def main():
    tester_func_2()


if __name__ == '__main__':
    main()
