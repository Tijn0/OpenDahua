from struct import pack

from opendahua.ptcp.ptcp_packet_body import PtcpPacketBody
from opendahua.ptcp.ptcp_packet_identifier import PtcpPacketIdentifier


class PtcpPacket:
    # Header constants.
    HEADER_MAGIC_PTCP = b"PTCP"
    
    # Format constants.
    FORMAT_HEADER_PACK = "!4sLLLLL"
    FORMAT_PTCP_PACKET_STRING = "PTCP(rlid={offset_sent:08}, llid={offset_received:08}, pid={packet_identifier:08}, lmid={packet_identifier_local:08}, rmid={packet_identifier_local_received_last:08}, body={body})"
    
    def __init__(
            self,
            offset_sent: int,
            offset_received: int,
            packet_identifier: PtcpPacketIdentifier,
            packet_identifier_local: PtcpPacketIdentifier,
            packet_identifier_local_received_last: PtcpPacketIdentifier,
            body: PtcpPacketBody,
    ) -> None:
        self._offset_sent: int = offset_sent
        self._offset_received: int = offset_received
        self._packet_identifier: PtcpPacketIdentifier = packet_identifier
        self._packet_identifier_local: PtcpPacketIdentifier = packet_identifier_local
        self._packet_identifier_local_received_last: PtcpPacketIdentifier = packet_identifier_local_received_last
        self._body: PtcpPacketBody = body
    
    # TODO: apart header type maken.
    def _get_header_bytes(self) -> bytes:
        return pack(
            self.FORMAT_HEADER_PACK,
            self.HEADER_MAGIC_PTCP,
            self._offset_sent,
            self._offset_received,
            self._packet_identifier.get_ptcp_packet_identifier_int(),
            self._packet_identifier_local.get_ptcp_packet_identifier_int(),
            self._packet_identifier_local_received_last.get_ptcp_packet_identifier_int(),
        )

    def get_ptcp_packet_bytes(self) -> bytes:
        return self._get_header_bytes() + self._body.get_ptcp_packet_body_bytes()
    
    def get_body(self) -> PtcpPacketBody:
        return self._body
    
    def get_packet_identifier(self) -> PtcpPacketIdentifier:
        """Get the pid from the PTCP packet."""
        return self._packet_identifier
    
    def get_packet_identifier_local_received_last(self) -> PtcpPacketIdentifier:
        """Get the rmid from the PTCP packet."""
        return self._packet_identifier_local_received_last
    
    def get_packet_identifier_local(self) -> PtcpPacketIdentifier:
        """Get the lmid from the PTCP packet."""
        return self._packet_identifier_local
    
    def get_offset_sent(self) -> int:
        """Get the rlid from the PTCP packet."""
        return self._offset_sent
    
    def get_offset_received(self) -> int:
        """Get the llid from the PTCP packet."""
        return self._offset_received
    
    def __str__(self) -> str:
        return self.FORMAT_PTCP_PACKET_STRING.format(
            offset_sent=self._offset_sent,
            offset_received=self._offset_received,
            packet_identifier=self._packet_identifier.get_ptcp_packet_identifier_int(),
            packet_identifier_local=self._packet_identifier_local.get_ptcp_packet_identifier_int(),
            packet_identifier_local_received_last=self._packet_identifier_local_received_last.get_ptcp_packet_identifier_int(),
            body=self._body.get_ptcp_packet_body_bytes(),
        )
