from Py106.MsgDecode1553 import *
from Py106.time import Time
import Py106.packet as packet
import Py106.status as status


class Message:
    # -----------------------------------------------------------------------------------
    class Header_ch10:
        def __init__(self, pkt_hdr: packet.Header):
            # self.msg_error = msg.p1553Hdr.contents.Field.BlockStatus.MsgError
            self.adapter_id = pkt_hdr.ch_id
            self.data_type = packet.DataType.MIL1553_FMT_1
            # self.time_tag = msg.p1553Hdr.contents.Field.PktTime
            self.serial = pkt_hdr.seq_num
            self.data_len = pkt_hdr.data_len
            self.flags = pkt_hdr.packet_flags

        def to_dict(self) -> dict:
            return \
                {
                    # 'MSG_STATUS': c.FIX_STATUS if not self.msg_error else c.NOT_FIX_STATUS,
                    'ADAPTER_ID': format(self.adapter_id, "04x"),
                    'DATA_TYPE': format(self.data_type, "04x"),
                    # 'TIME_TAG': format(self.time_tag, "016x"),
                    'SERIAL': format(self.serial, "08x"),
                    'DATA_LENGTH': format(self.data_len, "08x"),
                    'HEADER_FLAGS': format(self.flags, "02x")
                }

    # -----------------------------------------------------------------------------------
    class Header_1553:
        T_R = ("R", "T")

        @property
        def bus_id(self) -> int:
            # BUS 'A'-> 0 ; BUS 'B' -> 1
            return chr(ord('A') + self._recorde.p1553Hdr.contents.Field.BlockStatus.BusID)

        @property
        def rt_to_rt(self) -> bool:
            # TODO: write docstring about it
            return self._record.p1553Hdr.contents.Field.BlockStatus.RT2RT != 0

        @staticmethod
        def get_dict(**args: object) -> dict:
            """
            @param args: json keys and values
            @return: dict
            """
            return args

        @staticmethod
        def decode_command_word(cmd: CmdWord_Fields):
            return cmd.Field.RTAddr, cmd.Field.SubAddr

        @staticmethod
        def to_hex(sts: StatWord, cmd: CmdWord):
            return format(cmd.contents.Value, "04x"), format(sts.contents.Value, "04x")

        def __init__(self, record: CurrMsg_1553F1, decoder: Decode1553F1):
            # TODO: add time_tag and msg_status to this class
            self._record: CurrMsg_1553F1 = record

            # decoding first command word
            # TODO: check typehint in decode_command_word
            self.tr_1, self.sa_1 = self.decode_command_word(self._recorde.pCmdWord1.contents.Field)
            self.word_count = decoder.word_cnt(self._recorde.pCmdWord1.contents.Value)

            # checking transmit or receive mode
            self.tr_or_rec = self.T_R[self._recorde.pCmdWord1.contents.Field.TR]

            # getting hex value of command and status word
            self.cmd1_value, self.status1_value = self.to_hex(self._recorde.pStatWord1,
                                                              self._recorde.pCmdWord1)

            # assuming that it's a transmit / receive message
            tr_2 = None
            sa_2 = None
            cmd_word_2 = None
            status_word_2 = None

            # checking for rt2rt communicate messages
            if self.rt_to_rt:
                tr_2 = record.pCmdWord2.contents.Field.RTAddr
                sa_2 = record.pCmdWord2.contents.Field.SubAddr
                cmd_word_2 = format(record.pCmdWord2.contents.Value, "04x")
                status_word_2 = format(record.pStatWord2.contents.Value, "04x")
                tr_or_rec = "RT -> RT"

            if record.p1553Hdr.contents.Field.BlockStatus.MsgError == 0:
                self.data_words = list(map(lambda x: format(x, "04x"), record.pData.contents))
            else:
                self.data_words = 'Msg Error'

        def to_dict(self) -> dict:
            return self.get_dict(
                ADAPTER_ID=3
            )

    # -----------------------------------------------------------------------------------
    class Data_1553:
        # TODO: implement class
        pass

    # -----------------------------------------------------------------------------------
    def __init__(self, pkt_hdr: packet.Header, msg: CurrMsg_1553F1, decoder_1553: Decode1553F1) -> None:
        self._header_ch10 = self.Header_ch10(pkt_hdr).to_dict()
        self._header_1553 = Message.get_1553_header(pkt_hdr, msg)
        self._content_1553 = body_1553_msg(msg, decoder_1553)

    # -----------------------------------------------------------------------------------
    @staticmethod
    def get_1553_header(pkt_hdr: object, msg: object) -> dict:
        """
                @param content: object. contains all the 1553 msg in packet
                @param decoder_1553: the tool to decode the info in packet
                @return: dict
                """

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
