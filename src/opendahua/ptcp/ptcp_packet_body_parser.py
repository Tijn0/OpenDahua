from opendahua.ptcp.ptcp_packet_body import PtcpPacketBody
from opendahua.ptcp.ptcp_packet_body_connection_status import PtcpPacketBodyPortBindConnectionStatus
from opendahua.ptcp.ptcp_packet_body_data import PtcpPacketBodyData
from opendahua.ptcp.ptcp_packet_body_empty import PtcpPacketBodyEmpty
from opendahua.ptcp.ptcp_packet_body_heartbeat import PtcpPacketBodyHeartbeat
from opendahua.ptcp.ptcp_packet_body_syn import PtcpPacketBodySyn
from opendahua.ptcp.ptcp_packet_type import PtcpPacketType


class PtcpPacketBodyParser:
    # Error constants.
    ERROR_UNEXPECTED_PACKET_TYPE = "Unexpected packet type \"{packet_type:02X}\" for packet with body \"{packet_body}\"."

    # Index constants.
    INDEX_FIRST = 0
    
    @classmethod
    def parse(cls, body_bytes: bytes) -> PtcpPacketBody:
        if body_bytes == PtcpPacketBodyEmpty().get_ptcp_packet_body_bytes():
            return PtcpPacketBodyEmpty()
        else:
            packet_type_bytes = cls._determine_packet_type(body_bytes)
            
            match packet_type_bytes:
                case PtcpPacketType.DATA:
                    return PtcpPacketBodyData.create_from_bytes(body_bytes)
                case PtcpPacketType.SYN:
                    return PtcpPacketBodySyn()
                case PtcpPacketType.HEARTBEAT:
                    return PtcpPacketBodyHeartbeat()
                case PtcpPacketType.CONNECTION_STATUS:
                    return PtcpPacketBodyPortBindConnectionStatus(body_bytes)
                case _:
                    raise Exception(cls.ERROR_UNEXPECTED_PACKET_TYPE.format(packet_type=packet_type_bytes))
            
    @classmethod
    def _determine_packet_type(cls, body_bytes: bytes) -> PtcpPacketType:
        packet_type_bytes: int = body_bytes[cls.INDEX_FIRST]
        
        try:
            return PtcpPacketType(packet_type_bytes)
        except ValueError:
            raise Exception(cls.ERROR_UNEXPECTED_PACKET_TYPE.format(packet_type=packet_type_bytes, packet_body=body_bytes))
