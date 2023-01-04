import struct as s
import ijson as stream
import constants as c


<<<<<<< Updated upstream:source/writer.py
class Writer:
# ''' ---------------------------------------------------------------------------------------------------------'''
=======
class Message_Exalt:
    # ''' ---------------------------------------------------------------------------------------------------------'''
>>>>>>> Stashed changes:source/message_ex.py

    # ''' --------------------------------------------------------------------------------------'''
    # Constants for dictionary keys
    HEADER_MSG = 'HEADER_MSG'
    BODY_MSG = 'BODY_MSG'
<<<<<<< Updated upstream:source/writer.py
=======
    DATA_WORDS = 'DATA_WORDS'

>>>>>>> Stashed changes:source/message_ex.py
    # ''' --------------------------------------------------------------------------------------'''


    # ''' --------------------------------------------------------------------------------------'''
    # generic methods for class
    @staticmethod
    def convert_hex_array(values: list[str]) -> list[int]:
        # function will return a decimal values list
        for i, value in enumerate(values):
            values[i] = int(value, 16)
        return values
    # ''' --------------------------------------------------------------------------------------'''


    # ''' --------------------------------------------------------------------------------------'''
    # Header message functions
<<<<<<< Updated upstream:source/writer.py
    @staticmethod
    def header_bytes(record) -> bytes:
         # setting format bytes
=======
    def header_bytes(self, record) -> bytes:
        # setting format bytes
>>>>>>> Stashed changes:source/message_ex.py
        header_msg_format = ">B2HQ2LB"
        return s.pack(header_msg_format, *self.convert_hex_array(
            [value for _, value in record[Message_Exalt.HEADER_MSG].items()]))

    # ''' --------------------------------------------------------------------------------------'''


    # ''' --------------------------------------------------------------------------------------'''
    # Body message functions

    # TODO: future values requires (px status and 1553 flags) and MSG ERRORS treatment
    def content_bytes(self, record) -> tuple[bytes, str]:
        content_dict = record[Message_Exalt.BODY_MSG]

        content_bytes_format = '>5H{}HH'.format(len(content_dict[self.DATA_WORDS]))

        if len(content_dict[self.DATA_WORDS]) != 0 and content_dict[self.DATA_WORDS][0] != 'Msg Error':
            data_words_decimal = Message_Exalt.convert_hex_array(content_dict[self.DATA_WORDS])
        elif len(content_dict[self.DATA_WORDS]) == content_dict[self.DATA_WORDS] == 0:
            data_words_decimal = []
        else:
            data_words_decimal = c.MSG_ERROR

        data_bytes = s.pack(content_bytes_format,
                            int(content_dict['CW1'], 16),
                            int(content_dict['CW2'], 16) if content_dict['CW2'] is not None else int(c.NULL, 16),
                            int(content_dict['SW1'], 16),
                            int(content_dict['SW2'], 16) if content_dict['SW2'] is not None else int(c.NULL, 16),
                            5,  # px status
                            *data_words_decimal,
                            3)  # 1553 flags
        return data_bytes, content_bytes_format

    @staticmethod
    def write_content(record, file_position) -> None:
        # converting the info from record to byte object and getting its content format.
        content_data_bytes, content_format = Message_Exalt.content_bytes(record)

        with open(c.EXALT_FILE_PATH, "ab") as output:
            # TODO: check if file position pointer in the correct place
            output.write(content_data_bytes)                  
    # ''' --------------------------------------------------------------------------------------'''
# ''' ---------------------------------------------------------------------------------------------------------'''


def main():
    with open(c.EXALT_FILE_PATH, "rb") as f:
        for record in stream.items(f, "item"):
            print(Message_Exalt.content_bytes(record))
            # print([value for _, value in record['BODY_MSG'].items()])


if __name__ == '__main__':
    main()
