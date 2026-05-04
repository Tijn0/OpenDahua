import _queue
import threading
import time
from queue import Queue

from src.helpers import UDP
from src.logger import Logger
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
    # Error constants.
    ERROR_DATA_TOO_LARGE = "The data is too large. Fix me by implementing packet chunking."
    
    # Logging constants.
    LOGGING_DROPPING_NON_CONTIGUOUS_PACKET = "Dropping non contiguous packet."
    LOGGING_RETRANSMITTING_PACKET = "Retransmitting packet at offset {offset}"
    LOGGING_TRANSMIT = "TX: {packet}"
    LOGGING_RECEIVE = "RX: {packet}"

    # Time constants.
    TIME_NUMBER_OF_SECOND_HEARTBEAT_INTERVAL = 2

    # Timeout constants.
    TIMEOUT_NUMBER_OF_SECOND_RECEIVE = 0.01
    TIMEOUT_NUMBER_OF_SECOND_ACK = 0.20

    # Size constants.
    SIZE_BUFFER = 4096
    SIZE_MAXIMUM_DATA = 1280

    def __init__(self, socket_udp: UDP):
        self._socket_udp: UDP = socket_udp
        
        self._offset_sent = 0
        self._offset_received = 0
        self._number_of_packet_sent = 0
        self._packet_identifier_local = PtcpPacketIdentifier.ZERO()
        self._packet_identifier_local_received_last = PtcpPacketIdentifier.ZERO()
        self._realm_identifier = RealmIdentifier.create_random()

        self._all_packet_unacked = {}
        
        self._queue_receive: Queue[bytes] = Queue()
        self._queue_send: Queue[PtcpPacketBody] = Queue()
        
        self._time_heartbeat_last = time.time()
        
        self._connection_thread = threading.Thread(target=self._connection_loop, daemon=True)
        self._connection_thread.start()
    
    
    def send(self, data: bytes) -> None:
        if len(data) > self.SIZE_MAXIMUM_DATA:
            raise Exception(self.ERROR_DATA_TOO_LARGE)
        else:
            self._queue_send.put(PtcpPacketBodyData(self._realm_identifier, data))
    
    
    def recv(self, timeout: int|float = None) -> bytes:
        try:
            return self._queue_receive.get(timeout=timeout)
        except _queue.Empty:
            raise TimeoutError
        
        
    def _connection_loop(self) -> None:
        self._send_syn()
        
        while True:
            self._handle_receive()
            self._handle_send()
            self._handle_retransmit()
            self._handle_heartbeat()
        
        
    def _handle_receive(self) -> None:
        try:
            data = self._socket_udp.recv(self.SIZE_BUFFER, timeout=self.TIMEOUT_NUMBER_OF_SECOND_RECEIVE)
            
            packet = PtcpPacketParser.parse(data)
            
            Logger.debug(self.LOGGING_RECEIVE.format(packet=packet))
            
            self._handle_packet(packet)
        except TimeoutError:
            # Nothing to receive.
            return
    
    def _handle_packet(self, packet: PtcpPacket) -> None:
        self._packet_identifier_local_received_last = packet.get_packet_identifier_local()
        
        self._handle_ack(packet.get_offset_received())
        
        if packet.get_offset_sent() == self._offset_received:
            packet_body = packet.get_body()
            
            if isinstance(packet_body, PtcpPacketBodyData):
                self._queue_receive.put(packet_body.get_data_bytes())
            else:
                # Don't add non-data packets to the receive queue.
                pass
            
            self._offset_received += len(packet.get_body())
            
            if packet.get_body().is_empty():
                # Don't ack acks
                pass
            else:
                self._send_ack()
        
        else:
            Logger.warning(self.LOGGING_DROPPING_NON_CONTIGUOUS_PACKET)
            
            
    def _handle_ack(self, offset_acked: int) -> None:
        all_offset_acked: list[int] = [offset for offset in self._all_packet_unacked if offset <= offset_acked]
        
        for offset in all_offset_acked:
            del self._all_packet_unacked[offset]
        
        
    def _handle_send(self):
        if self._queue_send.empty():
            # Nothing to send.
            pass
        else:
            body = self._queue_send.get()
            
            packet = PtcpPacket(
                offset_sent=self._offset_sent,
                offset_received=self._offset_received,
                packet_identifier=self._determine_packet_identifier(),
                packet_identifier_local=self._packet_identifier_local,
                packet_identifier_local_received_last=self._packet_identifier_local_received_last,
                body=body,
            )
            
            self._send_packet(packet)
            
        
    def _send_syn(self) -> None:
        packet = PtcpPacket(
            offset_sent=self._offset_sent,
            offset_received=self._offset_received,
            packet_identifier=PtcpPacketIdentifier.SYN(),
            packet_identifier_local=self._packet_identifier_local,
            packet_identifier_local_received_last=self._packet_identifier_local_received_last,
            body=PtcpPacketBodySyn()
        )
        
        self._send_packet(packet)
    
    
    def send_bind(self, port: int) -> None:
        self._queue_send.put(PtcpPacketBodyBind(self._realm_identifier, port))
        
    
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
    
    
    def _add_packet_to_all_packet_unacked_if_needed(self, packet: PtcpPacket) -> None:
        if packet.get_body().is_empty():
            # Ack packets don't get acked.
            pass
        else:
            self._all_packet_unacked[self._offset_sent] = (packet, time.time())
    
    
    def _handle_retransmit(self) -> None:
        time_now = time.time()
        
        for offset, (packet, timestamp) in list(self._all_packet_unacked.items()):
            if time_now - timestamp > self.TIMEOUT_NUMBER_OF_SECOND_ACK:
                print(self.LOGGING_RETRANSMITTING_PACKET.format(offset=offset))
                self._socket_udp.send(packet.get_ptcp_packet_bytes())
                self._all_packet_unacked[offset] = (packet, time_now)
            else:
                # We are still waiting for an ack.
                pass
    
    
    def _handle_heartbeat(self) -> None:
        time_now = time.time()
        
        if time_now - self._time_heartbeat_last > self.TIME_NUMBER_OF_SECOND_HEARTBEAT_INTERVAL:
            self._send_heartbeat()
            self._time_heartbeat_last = time_now
        else:
            # Don't send heartbeat.
            pass


    def _send_heartbeat(self) -> None:
        self._queue_send.put(PtcpPacketBodyHeartbeat())
    
    
    def _send_packet(self, packet: PtcpPacket) -> None:
        body = packet.get_body()
        
        self._offset_sent += len(body)
        self._packet_identifier_local = self._packet_identifier_local.increment()
        
        self._update_number_of_packet_sent_if_needed(body)
        self._add_packet_to_all_packet_unacked_if_needed(packet)
        
        Logger.debug(self.LOGGING_TRANSMIT.format(packet=packet))
        
        self._socket_udp.send(packet.get_ptcp_packet_bytes())
    
    
    def _determine_packet_identifier(self) -> PtcpPacketIdentifier:
        return PtcpPacketIdentifier.create_maximum().subtract(self._number_of_packet_sent)
    
    
    def _update_number_of_packet_sent_if_needed(self, packet_body: PtcpPacketBody) -> None:
        if packet_body.is_empty():
            # Empty packets don't count.
            pass
        elif isinstance(packet_body, PtcpPacketBodySyn):
            # Syn packets don't count.
            pass
        else:
            self._number_of_packet_sent += 1
