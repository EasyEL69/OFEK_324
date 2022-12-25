from Py106.MsgDecode1553 import Decode1553F1
from Py106.time import Time
import Py106.packet as packet
import Py106.status as status
import json
import constants as c
import sys


class Message:
    def __init__(self, pkt_hdr: object, msg: object, decoder_1553: object) -> None:
        self._msg_1553 = \
            {
                'HEADER_MSG': Message.get_1553_header(pkt_hdr, msg),

                'BODY_MSG': body_1553_msg(msg, decoder_1553)
            }

    @staticmethod
    def get_1553_header(pkt_hdr: object, msg: object) -> dict:
        """
        @param pkt_hdr: Packet object that contain parts of 1553 header message info
        @param msg: part of the header of 1553 content can be found msg object (contain header and content)
        @return: None. function set header info to a dict
        """
        return get_dict(
            MSG_STATUS=c.FIX_STATUS if is_msg_fix(msg) else c.NOT_FIX_STATUS,
            ADAPTER_ID=format(pkt_hdr.ch_id, "04x"),  # pass
            DATA_TYPE=format(packet.DataType.MIL1553_FMT_1, "04x"),  # pass
            TIME_TAG=format(msg.p1553Hdr.contents.Field.PktTime, "016x"),
            SERIAL=format(pkt_hdr.seq_num, "08x"),
            DATA_LENGTH=format(pkt_hdr.data_len, "08x"),
            HEADER_FLAGS=format(pkt_hdr.packet_flags, "02x")
        )

    @staticmethod
    def get_content(content: object, decoder_1553: object) -> dict:
        """
        @param content: object. contains all the 1553 msg in packet
        @param decoder_1553: the tool to decode the info in packet
        @return: None
        """
        bus_id = ord(65 + content.p1553Hdr.contents.Field.BlockStatus.BusID)

        # getting info we need from command word
        tr_1, sa_1 = Message.decode_cmd(content.pCmdWord1.contents.Field)
        word_count = decoder_1553.word_cnt(content.pCmdWord1.contents.Value)

        # checking transmit or receive mode
        t_r = ("R", "T")
        tr_or_rec = t_r[content.pCmdWord1.contents.Field.TR]

        # getting hex value of command and status word
        cmd_word_1 = format(content.pCmdWord1.contents.Value, "04x")
        status_word_1 = format(content.pStatWord1.contents.Value, "04x")

        # assuming that it's a transmit / receive message
        tr_2 = None
        sa_2 = None
        cmd_word_2 = None
        status_word_2 = None

        # checking for rt2rt communicate messages
        if content.p1553Hdr.contents.Field.BlockStatus.RT2RT != 0:
            tr_2 = content.pCmdWord2.contents.Field.RTAddr
            sa_2 = content.pCmdWord2.contents.Field.SubAddr
            cmd_word_2 = format(content.pCmdWord2.contents.Value, "04x")
            status_word_2 = format(content.pStatWord2.contents.Value, "04x")
            tr_or_rec = "RT -> RT"

        # init data words array
        data_words = []

        if content.p1553Hdr.contents.Field.BlockStatus.MsgError == 0:
            for iDataIdx in range(word_count):
                data_words.append(format(content.pData.contents[iDataIdx], "04x"))
        else:
            data_words.append('Msg Error')

        # TODO: add additional 1553 flags

    @staticmethod
    def get_dict(**kwargs: object) -> dict:
        """
        @param args: json keys and values
        @return: dict
        """
        return kwargs

    @staticmethod
    def is_msg_fix(msg: object) -> bool:
        """
        @param msg:
        @return: Boolean. True if msg status is OK else False
        """
        return msg.p1553Hdr.contents.Field.BlockStatus.MsgError == 0

    @staticmethod
    def decode_cmd(contents):
        return contents.Field.RTAddr, contents.Field.SubAddr


def body_msg_dict(args) -> dict:
    return \
        {
            'BUS_ID': args[0],
            'TA1': args[1],
            'SA1': args[2],
            'TA2': args[3],
            'SA2': args[4],
            'TYPE': args[5],
            'CW1': args[6],
            'SW1': args[7],
            'CW2': args[8],
            'SW2': args[9],
            'WORD_CNT': args[10],
            'DATA_WORDS': args[11]
        }


def get_dict(**args: object) -> dict:
    """
    @param args: json keys and values
    @return: dict
    """
    return args


def is_msg_fix(msg: object) -> bool:
    """
    @param msg:
    @return: Boolean. True if msg status is OK else False
    """
    return msg.p1553Hdr.contents.Field.BlockStatus.MsgError == 0


def get_1553_header(pkt_hdr, msg) -> dict:
    return get_dict(
        MSG_STATUS=c.FIX_STATUS if is_msg_fix(msg) else c.NOT_FIX_STATUS,
        ADAPTER_ID=format(pkt_hdr.ch_id, "04x"),  # pass
        DATA_TYPE=format(packet.DataType.MIL1553_FMT_1, "04x"),  # pass
        TIME_TAG=format(msg.p1553Hdr.contents.Field.PktTime, "016x"),
        SERIAL=format(pkt_hdr.seq_num, "08x"),
        DATA_LENGTH=format(pkt_hdr.data_len, "08x"),
        HEADER_FLAGS=format(pkt_hdr.packet_flags, "02x")
    )


def body_1553_msg(msg, decoder_1553) -> dict:
    # busID A -> 0 or busID B -> 1
    bus_ID = ord(65 + msg.p1553Hdr.contents.Field.BlockStatus.BusID)

    # getting info we need from command word
    tr_1 = msg.pCmdWord1.contents.Field.RTAddr
    sa_1 = msg.pCmdWord1.contents.Field.SubAddr
    word_count = decoder_1553.word_cnt(msg.pCmdWord1.contents.Value)

    # checking transmit or receive mode
    t_r = ("R", "T")
    tr_or_rec = t_r[msg.pCmdWord1.contents.Field.TR]

    # getting hex value of command and status word
    cmd_word_1 = format(msg.pCmdWord1.contents.Value, "04x")
    status_word_1 = format(msg.pStatWord1.contents.Value, "04x")

    # assuming that it's a transmit / receive message
    tr_2 = None
    sa_2 = None
    cmd_word_2 = None
    status_word_2 = None

    # checking for rt2rt communicate messages
    if msg.p1553Hdr.contents.Field.BlockStatus.RT2RT != 0:
        tr_2 = msg.pCmdWord2.contents.Field.RTAddr
        sa_2 = msg.pCmdWord2.contents.Field.SubAddr
        cmd_word_2 = format(msg.pCmdWord2.contents.Value, "04x")
        status_word_2 = format(msg.pStatWord2.contents.Value, "04x")
        tr_or_rec = "RT -> RT"

    # init data words array
    data_words = []

    if msg.p1553Hdr.contents.Field.BlockStatus.MsgError == 0:
        for iDataIdx in range(word_count):
            data_words.append(format(msg.pData.contents[iDataIdx], "04x"))
    else:
        data_words.append('Msg Error')

    # TODO: add additional 1553 flags

    return body_msg_dict([bus_ID, tr_1, sa_1, tr_2, sa_2, tr_or_rec, cmd_word_1, status_word_1,
                          cmd_word_2, status_word_2, word_count, data_words])


def msg_1553(pkt_hdr, msg, decoder_1553) -> dict:
    return \
        {
            'HEADER_MSG': get_1553_header(pkt_hdr, msg),

            'BODY_MSG': body_1553_msg(msg, decoder_1553)
        }


def create_output_file(pkt_io, decode1553) -> None:
    with open(c.OUTPUT_FILE_PATH, "wt") as f:
        # opening an array of messages
        f.write("[\n")

        # scanning over all packets in file
        for pkt_hdr in pkt_io.packet_headers():
            # checking for 1553 data packet type
            if pkt_hdr.data_type == packet.DataType.MIL1553_FMT_1:
                # reading 1553 message data
                pkt_io.read_data()
                for msg in decode1553.msgs():
                    json.dump(msg_1553(pkt_hdr, msg, decode1553), f, indent=2)
                    f.write(",\n\t")
        # closing array of messages
        f.write("\n]")

    # now all we have to do is to delete the last ',' after the last message
    with open(c.OUTPUT_FILE_PATH, "rb+") as f:
        f.seek(-7, 2)
        f.write(bytes(" ".encode()))


def parse() -> None:
    """ inspired by an open source code parsing
            Created on Jan 4, 2012
            by author: rb45
        """

    # Make IRIG 106 library classes
    pkt_io = packet.IO()
    time_utils = Time(pkt_io)
    decode1553 = Decode1553F1(pkt_io)

    # open chapter 10 file
    open_status = pkt_io.open(c.C10_PATH, packet.FileMode.READ)
    if open_status != status.OK:
        print("Error opening data file: %s" % c.C10_PATH)
        sys.exit(1)
    else:
        # file is good to go. analyzing part
        time_sync_status = time_utils.sync_time(False, 0)
        if time_sync_status != status.OK:
            print("Sync Status = %s" % status.Message(time_sync_status))
            sys.exit(1)

        create_output_file(pkt_io, decode1553)


def main() -> None:
    parse()


if __name__ == '__main__':
    main()
