from src.ptcp.ptcp_packet_body import PtcpPacketBody


class PtcpPacketBodySyn(PtcpPacketBody):
    # Body constants.
    BODY_SYN = b"\x00\x03\x01\x00"
    
    def __init__(self):
        super().__init__(self.BODY_SYN)
    