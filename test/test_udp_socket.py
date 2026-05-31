import asyncio
import random

from opendahua.logger import Logger
from opendahua.object.address import Address
from opendahua.ptcp.ptcp_packet_parser import PtcpPacketParser
from opendahua.udp.udp_protocol import UdpProtocol
from opendahua.udp.udp_socket import UdpSocket


class TestUdpSocket(UdpSocket):
    # Packet drop rate constants.
    PACKET_DROP_RATE = 0.25
    
    @classmethod
    async def create_from_socket(cls, socket: UDP) -> UdpSocket:
        loop = asyncio.get_running_loop()
        
        address_remote = Address.create_from_ip_and_port(socket.rhost, socket.rport)
        
        protocol = UdpProtocol()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: protocol,
            sock=socket,
        )
        
        return TestUdpSocket(transport, protocol, address_remote)
    
    def send(self, data) -> None:
        if self._is_packet_ptcp(bytes(data)):
            if random.random() >= self.PACKET_DROP_RATE:
                super().send(data)
            else:
                # Simulate dropped packet
                packet = PtcpPacketParser.parse(bytes(data))
                Logger.debug("TX: Dropping {packet}".format(packet=packet))
        else:
            # Ignore non PTCP traffic.
            super().send(data)
        
        
    async def receive(self) -> bytes:
        data = await super().receive()

        if self._is_packet_ptcp(data):
            if random.random() >= self.PACKET_DROP_RATE:
                return data
            else:
                # Simulate dropped packet
                packet = PtcpPacketParser.parse(data)
                Logger.debug("RX: Dropping {packet}".format(packet=packet))
                
                return await self.receive()
        else:
            # Ignore non PTCP traffic.
            return data
    
    
    @staticmethod
    def _is_packet_ptcp(data: bytes) -> bool:
        try:
            PtcpPacketParser.parse(data)
            
            return True
        except:
            return False
