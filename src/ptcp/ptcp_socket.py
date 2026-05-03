from collections import deque

from src.helpers import UDP
from src.object.realm_identifier import RealmIdentifier
from src.ptcp.ptcp_packet import PtcpPacket
from src.ptcp.ptcp_packet_body import PtcpPacketBody
from src.ptcp.ptcp_packet_body_bind import PtcpPacketBodyBind
from src.ptcp.ptcp_packet_body_data import PtcpPacketBodyData
from src.ptcp.ptcp_packet_body_empty import PtcpPacketBodyEmpty
from src.ptcp.ptcp_packet_body_heartbeat import PtcpPacketBodyHeartbeat
from src.ptcp.ptcp_packet_body_syn import PtcpPacketBodySyn
from src.ptcp.ptcp_packet_identifier import PtcpPacketIdentifier
from src.ptcp.ptcp_packet_parser import PtcpPacketParser


class PtcpSocket:
    # Time constants.
    TIME_NUMBER_OF_SECOND_RECEIVE_INTERVAL = 0.001
    
    # Size constants.
    SIZE_BUFFER = 4096

    def __init__(self, socket_udp: UDP):
        self._socket_udp: UDP = socket_udp
        
        self._offset_sent = 0
        self._offset_received = 0
        self._number_of_packet_sent = 0
        self._packet_identifier_local = PtcpPacketIdentifier.ZERO()
        self._packet_identifier_local_received_last = PtcpPacketIdentifier.ZERO()
        
        self._packet_identifier_expected = PtcpPacketIdentifier.create_maximum()

        self._buffer = {}
        self._queue = deque([])

    def connect(self) -> None:
        self.send_syn()
        
    def receive(self, timeout: int|float = None) -> bytes:
        data = self._socket_udp.recv(self.SIZE_BUFFER, timeout=timeout)
    
        packet = PtcpPacketParser.parse(data)
        
        self._offset_received += len(packet.get_body())
        self._packet_identifier_local_received_last = packet.get_packet_identifier_local()
        
        # TODO: dit weghalen.
        print(f"RX: {packet}")

        self.handle_packet(packet)
        
        if packet.get_body().is_empty():
            # Don't ack acks
            pass
        else:
            self._send_ack()
        
        return packet.get_body().get_ptcp_packet_body_bytes()
        
    def handle_packet(self, packet: PtcpPacket) -> None:
        packet_identifier = packet.get_packet_identifier()
        
        if isinstance(packet.get_body(), PtcpPacketBodySyn):
            self._packet_identifier_expected = packet_identifier
            self._buffer = {}
        elif packet_identifier.get_ptcp_packet_identifier_int() == self._packet_identifier_expected.get_ptcp_packet_identifier_int():
            self._queue.append(packet)
            self._packet_identifier_expected = self._packet_identifier_expected.decrement()
            
            while self._packet_identifier_expected.get_ptcp_packet_identifier_int() in self._buffer:
                self._queue.append(self._buffer[self._packet_identifier_expected.get_ptcp_packet_identifier_int()])
                self._buffer.pop(self._packet_identifier_expected.get_ptcp_packet_identifier_int())
        else:
            self._buffer[packet_identifier.get_ptcp_packet_identifier_int()] = packet
            
    def send(self, data: bytes, realm_identifier: RealmIdentifier = None) -> None:
        if realm_identifier is None:
            realm_identifier = RealmIdentifier.ZERO()
        else:
            # Realm identifier already set.
            pass
        
        body = PtcpPacketBodyData(realm_identifier, data)
        
        packet = PtcpPacket(
            offset_sent=self._offset_sent,
            offset_received=self._offset_received,
            packet_identifier=self._determine_packet_identifier(),
            packet_identifier_local=self._packet_identifier_local,
            packet_identifier_local_received_last=self._packet_identifier_local_received_last,
            body=body,
        )

        self._send_packet(packet)
        
    def send_syn(self) -> None:
        packet = PtcpPacket(
            offset_sent=self._offset_sent,
            offset_received=self._offset_received,
            packet_identifier=PtcpPacketIdentifier.SYN(),
            packet_identifier_local=self._packet_identifier_local,
            packet_identifier_local_received_last=self._packet_identifier_local_received_last,
            body=PtcpPacketBodySyn()
        )
        
        self._send_packet(packet)
    
    def send_heartbeat(self) -> None:
        packet = PtcpPacket(
            offset_sent=self._offset_sent,
            offset_received=self._offset_received,
            packet_identifier=self._determine_packet_identifier(),
            packet_identifier_local=self._packet_identifier_local,
            packet_identifier_local_received_last=self._packet_identifier_local_received_last,
            body=PtcpPacketBodyHeartbeat()
        )
        
        self._send_packet(packet)
    
    def send_bind(self, realm_identifier: RealmIdentifier, port: int) -> None:
        packet = PtcpPacket(
            offset_sent=self._offset_sent,
            offset_received=self._offset_received,
            packet_identifier=self._determine_packet_identifier(),
            packet_identifier_local=self._packet_identifier_local,
            packet_identifier_local_received_last=self._packet_identifier_local_received_last,
            body=PtcpPacketBodyBind(realm_identifier, port),
        )
        
        self._send_packet(packet)
    
    def _send_ack(self) -> None:
        packet = PtcpPacket(
            offset_sent=self._offset_sent,
            offset_received=self._offset_received,
            packet_identifier=self._determine_packet_identifier(),
            packet_identifier_local=self._packet_identifier_local,
            packet_identifier_local_received_last=self._packet_identifier_local_received_last,
            body=PtcpPacketBodyEmpty()
        )
    
        self._send_packet(packet)
    
    def _send_packet(self, packet: PtcpPacket) -> None:
        body = packet.get_body()
        
        self._offset_sent += len(body)
        self._packet_identifier_local = self._packet_identifier_local.increment()
        
        self.update_number_of_packet_sent_if_needed(body)
        
        # TODO: dit weghalen
        print(f"TX: {packet}")
        
        self._socket_udp.send(packet.get_ptcp_packet_bytes())
    
    def _determine_packet_identifier(self) -> PtcpPacketIdentifier:
        return PtcpPacketIdentifier.create_maximum().subtract(self._number_of_packet_sent)

    def update_number_of_packet_sent_if_needed(self, packet_body: PtcpPacketBody) -> None:
        if packet_body.is_empty():
            # Empty packets don't count.
            pass
        elif isinstance(packet_body, PtcpPacketBodySyn):
            # Syn packets don't count.
            pass
        else:
            self._number_of_packet_sent += 1
   