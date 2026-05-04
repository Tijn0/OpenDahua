import random

from src.helpers import UDP
from src.logger import Logger
from src.ptcp.ptcp_packet_parser import PtcpPacketParser


class TestUdpSocket(UDP):
    # Packet drop rate constants.
    PACKET_DROP_RATE = 0.25
    
    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        
    def send(self, data) -> int:
        if self._is_packet_ptcp(bytes(data)):
            if random.random() >= self.PACKET_DROP_RATE:
                return super().send(data)
            else:
                # Simulate dropped packet
                packet = PtcpPacketParser.parse(bytes(data))
                Logger.debug("TX: Dropping {packet}".format(packet=packet))
                return 0
        else:
            # Ignore non PTCP traffic.
            return super().send(data)
        
    def recv(self, bufsize=4096, timeout=None):
        data = super().recv(bufsize=bufsize, timeout=timeout)

        if self._is_packet_ptcp(data):
            if random.random() >= self.PACKET_DROP_RATE:
                return data
            else:
                # Simulate dropped packet
                packet = PtcpPacketParser.parse(data)
                Logger.debug("RX: Dropping {packet}".format(packet=packet))
                raise TimeoutError
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
