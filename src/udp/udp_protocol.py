import asyncio


class UdpProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.packet_queue = asyncio.Queue()
        
    def connection_made(self, transport) -> None:
        pass
    
    def connection_lost(self, exc) -> None:
        pass
    
    def datagram_received(self, data, addr) -> None:
        self.packet_queue.put_nowait(data)
        