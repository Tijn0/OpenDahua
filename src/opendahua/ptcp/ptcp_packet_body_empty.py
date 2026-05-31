from opendahua.ptcp.ptcp_packet_body import PtcpPacketBody


class PtcpPacketBodyEmpty(PtcpPacketBody):
    # Body constants.
    BODY_EMPTY = b""
    
    def __init__(self):
        super().__init__(self.BODY_EMPTY)
