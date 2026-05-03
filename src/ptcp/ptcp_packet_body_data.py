from struct import pack

from src.object.realm_identifier import RealmIdentifier
from src.ptcp.ptcp_packet_body import PtcpPacketBody


class PtcpPacketBodyData(PtcpPacketBody):
    # Flag constants.
    FLAG_PACKET_DATA = 0x10000000

    # Format constants.
    FORMAT_HEADER = "!LLL"

    def __init__(self, realm_identifier: RealmIdentifier, payload: bytes):
        length = len(payload) | self.FLAG_PACKET_DATA
        ptcp_packet_body_bytes = pack(self.FORMAT_HEADER, length, realm_identifier.get_realm_identifier_int(), 0) + payload
        
        super().__init__(ptcp_packet_body_bytes)
    
    @classmethod
    def create_from_bytes(cls, body_bytes) -> PtcpPacketBodyData:
        from struct import unpack
        if len(body_bytes) < 12:
            raise ValueError("Body too short")
        
        length_with_flag, realm_int, pad = unpack(cls.FORMAT_HEADER, body_bytes[:12])
        
        length = length_with_flag & 0xFFFF
        payload = body_bytes[12:]
        
        if len(payload) != length:
            raise ValueError("Invalid length")
        
        return cls(RealmIdentifier(realm_int), payload)
    