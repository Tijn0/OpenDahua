from abc import ABC


class PtcpPacketBody(ABC):
    # Body constants.
    BODY_EMPTY = b""

    def __init__(self, ptcp_packet_body_bytes: bytes):
        self._ptcp_packet_body_bytes: bytes = ptcp_packet_body_bytes
        
    def get_ptcp_packet_body_bytes(self) -> bytes:
        return self._ptcp_packet_body_bytes
        
    def is_empty(self) -> bool:
        return self._ptcp_packet_body_bytes == self.BODY_EMPTY
    
    def __len__(self):
        return len(self._ptcp_packet_body_bytes)
        