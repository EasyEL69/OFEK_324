import struct as s
import ijson as stream
import constants as c


NULL = '0'
MSG_ERROR = [0]
BINARY_FILE = 'testing.bin'


class Writer:
# ''' ---------------------------------------------------------------------------------------------------------'''
    # Constants for dictionary keys
    HEADER_MSG = 'HEADER_MSG'
    BODY_MSG = 'BODY_MSG'

    # setting format bytes
    HEADER_MSG_FORMAT = ">B2HQ2LB"

    @staticmethod
    def convert_hex_array(values: list[str]) -> list[int]:
        # function will return a decimal values list
        for i, value in enumerate(values):
            values[i] = int(value, 16)
        return values

    # ''' --------------------------------------------------------------------------------------'''
    # Body message functions

    @staticmethod
    # TODO: future values requires (px status and 1553 flags) and MSG ERRORS treatment
    def content_bytes(record) -> tuple[bytes, str]:
        content_dict = record[Writer.BODY_MSG]

        content_bytes_format = '>5H{}HH'.format(len(content_dict['DATA_WORDS']))

        if len(content_dict["DATA_WORDS"]) != 0 and content_dict["DATA_WORDS"][0] != 'Msg Error':
            data_words_decimal = Writer.convert_hex_array(content_dict["DATA_WORDS"])
        elif len(content_dict["DATA_WORDS"]) == content_dict["WORD_CNT"] == 0:
            data_words_decimal = []
        else:
            data_words_decimal = MSG_ERROR

        data_bytes = s.pack(content_bytes_format,
                            int(content_dict['CW1'], 16),
                            int(content_dict['CW2'], 16) if content_dict['CW2'] is not None else int(NULL, 16),
                            int(content_dict['SW1'], 16),
                            int(content_dict['SW2'], 16) if content_dict['SW2'] is not None else int(NULL, 16),
                            5,  # px status
                            *data_words_decimal,
                            3)  # 1553 flags
        return data_bytes, content_bytes_format

    @staticmethod
    def write_content(record, file_position) -> None:
        # converting the info from record to byte object and getting its content format.
        content_data_bytes, content_format = Writer.content_bytes(record)

        with open(BINARY_FILE, "ab") as output:
            # TODO: check if file position pointer in the correct place
            output.write(content_data_bytes)

    # ''' --------------------------------------------------------------------------------------'''
    # Header message functions
    @staticmethod
    def header_bytes(record) -> bytes:
        return s.pack(Writer.HEADER_MSG_FORMAT, *Writer.convert_hex_array(
            [value for _, value in record[Writer.HEADER_MSG].items()]))

    # ''' --------------------------------------------------------------------------------------'''

# ''' ---------------------------------------------------------------------------------------------------------'''
def main():
    with open(c.OUTPUT_FILE_PATH, "rb") as f:
        for record in stream.items(f, "item"):
            print(Writer.content_bytes(record))
            # print([value for _, value in record['BODY_MSG'].items()])


if __name__ == '__main__':
    main()
