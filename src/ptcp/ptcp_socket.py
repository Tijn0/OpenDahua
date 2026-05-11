import asyncio

from src.logger import Logger
from src.ptcp.ptcp_packet import PtcpPacket
from src.ptcp.ptcp_packet_body import PtcpPacketBody
from src.ptcp.ptcp_packet_body_bind import PtcpPacketBodyBind
from src.ptcp.ptcp_packet_body_data import PtcpPacketBodyData
from src.ptcp.ptcp_packet_body_empty import PtcpPacketBodyEmpty
from src.ptcp.ptcp_packet_body_heartbeat import PtcpPacketBodyHeartbeat
from src.ptcp.ptcp_packet_body_syn import PtcpPacketBodySyn
from src.ptcp.ptcp_packet_identifier import PtcpPacketIdentifier
from src.ptcp.ptcp_packet_parser import PtcpPacketParser
from src.ptcp.ptcp_realm_identifier import PtcpRealmIdentifier
from src.udp.udp_socket import UdpSocket


class PtcpSocket:
    # Error constants.
    ERROR_SIZE_DATA_EXCEEDING_MAXIMUM = "The data is too large. Fix me by implementing packet chunking."
    
    # Logging constants.
    LOGGING_BUFFERING_NON_CONTIGUOUS_PACKET = "Buffering non contiguous packet."
    LOGGING_DROPPING_RETRANSMIT = "Dropping received retransmitted packet."
    LOGGING_RETRANSMITTING_PACKET = "Retransmitting packet at offset {offset}"
    LOGGING_CONNECTING = "[PTCP] Connecting."
    LOGGING_DISCONNECTING = "[PTCP] Disconnecting."
    LOGGING_TRANSMIT = "TX: {packet}"
    LOGGING_RECEIVE = "RX: {packet}"

    # Time constants.
    TIME_NUMBER_OF_SECOND_HEARTBEAT_INTERVAL = 5

    # Timeout constants.
    TIMEOUT_NUMBER_OF_SECOND_ACK = 0.50

    # Size constants.
    SIZE_DATA_MAXIMUM = 1280

    def __init__(self, udp_socket: UdpSocket):
        self._udp_socket: UdpSocket = udp_socket
        
        self._offset_sent = 0
        self._offset_received = 0
        self._packet_identifier = PtcpPacketIdentifier.create_maximum()
        self._packet_identifier_local = PtcpPacketIdentifier.ZERO()
        self._packet_identifier_local_received_last = PtcpPacketIdentifier.ZERO()
        self._realm_identifier = PtcpRealmIdentifier.create_random()

        self._all_packet_unacked = {}
        
        self._queue_receive: asyncio.Queue[bytes] = asyncio.Queue()
        self._queue_send: asyncio.Queue[PtcpPacketBody] = asyncio.Queue()
        
        self._buffer_receive: dict[int, PtcpPacket] = {}
        
        self._all_task = []
        
        
    async def connect(self) -> None:
        Logger.debug(self.LOGGING_CONNECTING)
        
        self._send_syn()
        self._all_task = [
            asyncio.create_task(self._loop_send()),
            asyncio.create_task(self._loop_receive()),
            asyncio.create_task(self._loop_retransmit()),
            asyncio.create_task(self._loop_heartbeat()),
        ]
        
        # TODO: wacht tot verbinding bevestigd is van de andere kant.
    
    async def _loop_send(self) -> None:
        while True:
            body = await self._queue_send.get()
            self._send_body(body)
    
    
    async def _loop_receive(self) -> None:
        while True:
            data = await self._udp_socket.receive()
            self._handle_receive(data)
    
    
    async def _loop_retransmit(self) -> None:
        while True:
            await asyncio.sleep(self.TIMEOUT_NUMBER_OF_SECOND_ACK)
            self._handle_retransmit()
    
    
    async def _loop_heartbeat(self) -> None:
        while True:
            await asyncio.sleep(self.TIME_NUMBER_OF_SECOND_HEARTBEAT_INTERVAL)
            self._send_heartbeat()
    
    
    def send(self, data: bytes) -> None:
        if len(data) > self.SIZE_DATA_MAXIMUM:
            raise Exception(self.ERROR_SIZE_DATA_EXCEEDING_MAXIMUM)
        else:
            self._queue_send.put_nowait(PtcpPacketBodyData(self._realm_identifier, data))
    
    
    async def receive(self) -> bytes:
        return await self._queue_receive.get()
        
        
    def _handle_receive(self, data: bytes) -> None:
        packet = PtcpPacketParser.parse(data)
        
        Logger.debug(self.LOGGING_RECEIVE.format(packet=packet))
        
        self._handle_packet(packet)
    
    
    def _handle_packet(self, packet: PtcpPacket) -> None:
        self._update_packet_identifier_local_received_last_if_needed(packet)
        self._handle_ack(packet.get_offset_received())
        
        offset = packet.get_offset_sent()
        
        if offset == self._offset_received:
            self._buffer_receive[offset] = packet
        elif offset > self._offset_received:
            Logger.warning(self.LOGGING_BUFFERING_NON_CONTIGUOUS_PACKET)
            self._buffer_receive[offset] = packet
        else:
            Logger.warning(self.LOGGING_DROPPING_RETRANSMIT)
            
        self._drain_receive_buffer()
        
    
    def _drain_receive_buffer(self) -> None:
        while self._offset_received in self._buffer_receive:
            packet = self._buffer_receive.pop(self._offset_received)
            packet_body = packet.get_body()
            
            if isinstance(packet_body, PtcpPacketBodyData):
                self._queue_receive.put_nowait(packet_body.get_data_bytes())
            else:
                # Don't add non-data packets to the receive queue.
                pass
            
            self._offset_received += len(packet.get_body())
            
            if packet.get_body().is_empty():
                # Don't ack acks.
                pass
            else:
                self._send_ack()


    def _update_packet_identifier_local_received_last_if_needed(self, packet: PtcpPacket) -> None:
        if packet.get_body().is_empty():
            # Acks don't count as last seen packet identifiers.
            pass
        else:
            self._packet_identifier_local_received_last = packet.get_packet_identifier_local()


    def _handle_ack(self, offset_acked: int) -> None:
        all_offset_acked: list[int] = [offset for offset in self._all_packet_unacked if offset <= offset_acked]
        
        for offset in all_offset_acked:
            del self._all_packet_unacked[offset]
        
        
    def _send_body(self, body: PtcpPacketBody) -> None:
        packet = PtcpPacket(
            offset_sent=self._offset_sent,
            offset_received=self._offset_received,
            packet_identifier=self._packet_identifier,
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
        self._realm_identifier = PtcpRealmIdentifier.create_random()
        
        self._queue_send.put_nowait(PtcpPacketBodyBind(self._realm_identifier, port))
        
    
    def _send_ack(self) -> None:
        packet = PtcpPacket(
            offset_sent=self._offset_sent,
            offset_received=self._offset_received,
            packet_identifier=self._packet_identifier,
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
            time_sent = asyncio.get_event_loop().time()
            
            self._all_packet_unacked[self._offset_sent] = (packet, time_sent)
    
    
    def _handle_retransmit(self) -> None:
        time_now = asyncio.get_event_loop().time()
        
        for offset, (packet, time_sent) in list(self._all_packet_unacked.items()):
            if time_now - time_sent > self.TIMEOUT_NUMBER_OF_SECOND_ACK:
                Logger.warning(self.LOGGING_RETRANSMITTING_PACKET.format(offset=offset))
                self._udp_socket.send(packet.get_ptcp_packet_bytes())
                self._all_packet_unacked[offset] = (packet, time_now)
            else:
                # We are still waiting for an ack.
                pass
    

    def _send_heartbeat(self) -> None:
        self._queue_send.put_nowait(PtcpPacketBodyHeartbeat())
    
    
    def _send_packet(self, packet: PtcpPacket) -> None:
        body = packet.get_body()
        
        self._offset_sent += len(body)
        self._packet_identifier_local = self._packet_identifier_local.increment()
        
        self._update_packet_identifier_if_needed(body)
        self._add_packet_to_all_packet_unacked_if_needed(packet)
        
        Logger.debug(self.LOGGING_TRANSMIT.format(packet=packet))
        
        self._udp_socket.send(packet.get_ptcp_packet_bytes())
    
    
    def _update_packet_identifier_if_needed(self, packet_body: PtcpPacketBody) -> None:
        if packet_body.is_empty():
            # Empty packets don't count.
            pass
        elif isinstance(packet_body, PtcpPacketBodySyn):
            # Syn packets don't count.
            pass
        else:
            self._packet_identifier = self._packet_identifier.decrement()


    async def disconnect(self) -> None:
        Logger.debug(self.LOGGING_DISCONNECTING)
        
        for task in self._all_task:
            task.cancel()
            
        await asyncio.gather(*self._all_task, return_exceptions=True)
        
        self._udp_socket.close()
