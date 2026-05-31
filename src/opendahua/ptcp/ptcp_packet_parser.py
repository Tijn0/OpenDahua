from struct import unpack

from opendahua.ptcp.ptcp_packet import PtcpPacket
from opendahua.ptcp.ptcp_packet_body_parser import PtcpPacketBodyParser
from opendahua.ptcp.ptcp_packet_identifier import PtcpPacketIdentifier


class PtcpPacketParser:
    # Error constants.
    ERROR_COULD_NOT_PARSE_PACKET = "Could not parse packet."
    ERROR_PACKET_TOO_SHORT = "Packet is too short"
    ERROR_INVALID_MAGIC = "Invalid magic \"{magic}\""

    # Format constants.
    FORMAT_HEADER = "!4sLLLLL"

    # Magic constants.
    MAGIC_PTCP = b"PTCP"
    
    # Size constants.
    SIZE_PACKET_MINIMUM = 24
    
    # Offset constants.
    OFFSET_BODY = 24

    @classmethod
    def parse(cls, packet_bytes: bytes) -> PtcpPacket:
        cls._assert_packet_size_is_valid(packet_bytes)
        
        header_bytes = packet_bytes[:cls.OFFSET_BODY]
        body_bytes = packet_bytes[cls.OFFSET_BODY:]

        magic, offset_sent, offset_received, packet_identifier, packet_identifier_local, packet_identifier_local_received_last = unpack(cls.FORMAT_HEADER, header_bytes)
        
        cls._assert_magic_is_valid(magic)
        
        return PtcpPacket(
            offset_sent=offset_sent,
            offset_received=offset_received,
            packet_identifier=PtcpPacketIdentifier(packet_identifier),
            packet_identifier_local=PtcpPacketIdentifier(packet_identifier_local),
            packet_identifier_local_received_last=PtcpPacketIdentifier(packet_identifier_local_received_last),
            body=PtcpPacketBodyParser.parse(body_bytes),
        )
    
    @classmethod
    def _assert_packet_size_is_valid(cls, packet_bytes: bytes) -> None:
        if len(packet_bytes) < 24:
            raise Exception(cls.ERROR_PACKET_TOO_SHORT)
        else:
            # All good.
            return None
        
    @classmethod
    def _assert_magic_is_valid(cls, magic: bytes) -> None:
        if magic == cls.MAGIC_PTCP:
            # All good.
            return None
        else:
            raise Exception(cls.ERROR_INVALID_MAGIC.format(magic=magic))
