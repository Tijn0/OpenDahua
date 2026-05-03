from enum import Enum


class PtcpPacketType(Enum):
    DATA = 0x10
    SYN = 0x00
    HEARTBEAT = 0x13
    CONNECTION_STATUS = 0x12
