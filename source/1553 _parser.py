try:
    from source.Py106.MsgDecode1553 import Decode1553F1
    from source.Py106.time import Time
    import source.Py106.packet as packet
    import source.Py106.status as status
    from pathlib import Path
    import json
    import sys
    import constants as c
except ImportError:
    raise ImportError


def header_msg_dict(args) -> dict:
    return \
        {
            'MSG_STATUS': args[0],
            'ADAPTER_ID': args[1],
            'DATA_TYPE': args[2],
            'TIME_TAG': args[3],
            'SERIAL': args[4],
            'DATA_LENGTH': args[5],
            'HEADER_FLAGS': args[6]
        }


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


def header_1553_msg(pkt_hdr, msg) -> dict:
    # check if msg is fixed
    msg_sts = format(0x11, "02x") if msg.p1553Hdr.contents.Field.BlockStatus.MsgError == 0 else format(0x1, "02x")

    # getting adapter ID
    adapter_id = format(pkt_hdr.ch_id, "04x")

    # 1553 data type
    data_type = format(packet.DataType.MIL1553_FMT_1, "04x")

    time_tagging = format(msg.p1553Hdr.contents.Field.PktTime, "016x")

    seq_num = format(pkt_hdr.seq_num, "08x")

    data_len = format(pkt_hdr.data_len, "08x")

    msg_header_flags = format(pkt_hdr.packet_flags, "02x")

    return header_msg_dict([msg_sts, adapter_id, data_type, time_tagging, seq_num, data_len, msg_header_flags])


def body_1553_msg(msg, decoder_1553) -> dict:
    # busID A -> 0 or busID B -> 1
    bus_id = 'B' if msg.p1553Hdr.contents.Field.BlockStatus.BusID == 1 else 'A'

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

    # checking for rt to rt communicate messages
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

    return body_msg_dict([bus_id, tr_1, sa_1, tr_2, sa_2, tr_or_rec, cmd_word_1, status_word_1,
                          cmd_word_2, status_word_2, word_count, data_words])


def msg_1553(pkt_hdr, msg, decoder_1553) -> dict:
    return \
        {
            'HEADER_MSG': header_1553_msg(pkt_hdr, msg),

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
