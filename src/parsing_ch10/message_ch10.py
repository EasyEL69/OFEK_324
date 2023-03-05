import src.parsing_ch10.Py106.packet as packet
from src.parsing_ch10.Py106.MsgDecode1553 \
    import StatWord, CmdWord, CurrMsg_1553F1, Decode1553F1

from typing import Tuple, Optional


class Message:
    # -----------------------------------------------------------------------------------
    class Header_ch10:
        def __init__(self, pkt_hdr: packet.Header):
            self.adapter_id = pkt_hdr.ch_id
            self.data_type = packet.DataType.MIL1553_FMT_1
            self.serial = pkt_hdr.seq_num
            self.data_len = pkt_hdr.data_len
            self.flags = pkt_hdr.packet_flags

        def to_dict(self) -> dict:
            return \
                {
                    'ADAPTER_ID': '0x' + str(format(self.adapter_id, "04x")).upper(),
                    'DATA_TYPE': '0x' + str(format(self.data_type, "04x")).upper(),
                    'SERIAL': '0x' + str(format(self.serial, "08x")).upper(),
                    'DATA_LENGTH': '0x' + str(format(self.data_len, "08x")).upper(),
                    'HEADER_FLAGS': '0x' + str(format(self.flags, "02x")).upper()
                }

    # -----------------------------------------------------------------------------------
    class Header_1553:
        T_R = ("R", "T")

        @property
        def bus_id(self) -> str:
            # BUS 'A'-> 0 ; BUS 'B' -> 1
            return chr(ord('A') + self._record.p1553Hdr.contents.Field.BlockStatus.BusID)

        @property
        def rt_to_rt(self) -> bool:
            return self._record.p1553Hdr.contents.Field.BlockStatus.RT2RT != 0

        @property
        def message_status(self) -> int:
            return not self._record.p1553Hdr.contents.Field.BlockStatus.MsgError

        @staticmethod
        def dict(**args) -> dict:
            """
            @param args: json keys and values
            @return: dict
            """
            return args

        @staticmethod
        def decode_command_word(cmd: CmdWord) -> Optional[Tuple[int, int]]:
            return cmd.Field.RTAddr, cmd.Field.SubAddr

        @staticmethod
        def to_hex(cmd: CmdWord, sts: StatWord) -> Optional[Tuple[str, str]]:
            return '0x' + str(format(cmd.Value, "04x")).upper(), '0x' + str(
                format(sts.Value, "04x")).upper()

        def __init__(self, record: CurrMsg_1553F1, decoder: Decode1553F1):

            self._record: CurrMsg_1553F1 = record

            self.time_tag = self._record.p1553Hdr.contents.Field.PktTime

            self.tr_1, self.sa_1 = self.decode_command_word(self._record.pCmdWord1.contents)
            self.word_count = decoder.word_cnt(self._record.pCmdWord1.contents.Value)

            # checking transmit or receive mode
            self.tr_or_rec = self.T_R[self._record.pCmdWord1.contents.Field.TR]

            # getting hex value of command and status word
            self.cmd1_value, self.status1_value = self.to_hex(self._record.pCmdWord1.contents,
                                                              self._record.pStatWord1.contents)

            # assuming that it's a transmit / receive message
            if self._record.pCmdWord2 and self._record.pStatWord2:
                self.tr_2, self.sa_2 = self.decode_command_word(self._record.pCmdWord2.contents)
                self.cmd2_value, self.status2_value = self.to_hex(self._record.pCmdWord2.contents,
                                                                  self._record.pStatWord2.contents)

            else:
                self.tr_2, self.sa_2 = None, None
                self.cmd2_value, self.status2_value = None, None

        def to_dict(self) -> dict:
            return self.dict(
                TIME_TAG=self.time_tag,
                COMMAND_WORD_1={'VALUE': self.cmd1_value, 'TR_1': self.tr_1, 'SA_1': self.sa_1},
                COMMAND_WORD_2={'VALUE': self.cmd2_value, 'TR_2': self.tr_2, 'SA_2': self.sa_2},
                STATUS_WORD_1=self.status1_value,
                STATUS_WORD_2=self.status2_value,
                WORD_COUNT=self.word_count,
                TRANSMIT_OR_RECEIVE=self.tr_or_rec,
                MESSAGE_STATUS=self.message_status
            )

    # -----------------------------------------------------------------------------------
    class Data_1553:
        def __init__(self, record: CurrMsg_1553F1):
            if record.p1553Hdr.contents.Field.BlockStatus.MsgError == 0:
                self.data_words = list(map(lambda x: '0x' + str(format(x, "04x")).upper(), record.pData.contents))
            else:
                self.data_words = 'Msg Error'

        @staticmethod
        def dict(**args) -> dict:
            """
            @param args: json keys and values
            @return: dict
            """
            return args

        def to_dict(self) -> dict:
            return self.dict(DATA_WORDS=self.data_words)

    # -----------------------------------------------------------------------------------
    def __init__(self, pkt_hdr: packet.Header, msg: CurrMsg_1553F1, decoder_1553: Decode1553F1) -> None:
        self.header_ch10 = self.Header_ch10(pkt_hdr)
        self.header_1553 = self.Header_1553(msg, decoder_1553)
        self.content_1553 = self.Data_1553(msg)

    def to_dict(self) -> dict:
        return \
            {
                'HEADER_CH10': self.header_ch10.to_dict(),
                'HEADER_1553': self.header_1553.to_dict(),
                'CONTENT_1553': self.content_1553.to_dict(),
            }

# -----------------------------------------------------------------------------------
