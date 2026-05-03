from src.ptcp.ptcp_packet_body import PtcpPacketBody


class PtcpPacketBodyHeartbeat(PtcpPacketBody):
    # Body constants.
    BODY_HEARTBEAT = b"\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    
    def __init__(self):
        super().__init__(self.BODY_HEARTBEAT)
