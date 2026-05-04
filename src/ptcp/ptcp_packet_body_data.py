from struct import pack, unpack

from src.ptcp.ptcp_packet_body import PtcpPacketBody
from src.ptcp.ptcp_realm_identifier import PtcpRealmIdentifier


class PtcpPacketBodyData(PtcpPacketBody):
    # Flag constants.
    FLAG_PACKET_DATA = 0x10000000

    # Format constants.
    FORMAT_HEADER = "!LLL"

    def __init__(self, realm_identifier: PtcpRealmIdentifier, payload: bytes):
        length = len(payload) | self.FLAG_PACKET_DATA
        ptcp_packet_body_bytes = pack(self.FORMAT_HEADER, length, realm_identifier.get_ptcp_realm_identifier_int(), 0) + payload
        
        super().__init__(ptcp_packet_body_bytes)
    
    @classmethod
    def create_from_bytes(cls, body_bytes) -> PtcpPacketBodyData:
        # TODO: refactor deze zielige functie.
        if len(body_bytes) < 12:
            raise ValueError("Body too short")
        
        length_with_flag, realm_int, pad = unpack(cls.FORMAT_HEADER, body_bytes[:12])
        
        length = length_with_flag & 0xFFFF
        payload = body_bytes[12:]
        
        if len(payload) != length:
            raise ValueError("Invalid length")
        
        return cls(PtcpRealmIdentifier(realm_int), payload)
    
    def get_data_bytes(self) -> bytes:
        # TODO: refactor deze zielige functie.
        return self._ptcp_packet_body_bytes[12:]

