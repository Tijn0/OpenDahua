from struct import pack, unpack
import socket

from src.ptcp.ptcp_packet_body import PtcpPacketBody
from src.ptcp.ptcp_realm_identifier import PtcpRealmIdentifier


class PtcpPacketBodyBind(PtcpPacketBody):
    # Type constants.
    TYPE = 0x11
    
    # Ip constants.
    IP_LOOPBACK = "127.0.0.1"
    
    # Format constants.
    FORMAT = "!B3xLLLL"
    
    # Padding constants.
    PADDING = 0
    
    def __init__(
        self,
        realm_identifier: PtcpRealmIdentifier,
        port: int,
        ip: str = IP_LOOPBACK,
    ):
        ip_int = self._ip_to_int(ip)

        body = pack(
            self.FORMAT,
            self.TYPE,
            realm_identifier.get_ptcp_realm_identifier_int(),
            self.PADDING,
            port,
            ip_int,
        )

        super().__init__(body)

    @staticmethod
    def _ip_to_int(ip: str) -> int:
        return int.from_bytes(socket.inet_aton(ip), "big")
    