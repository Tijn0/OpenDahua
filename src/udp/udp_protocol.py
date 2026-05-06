import asyncio
from asyncio import DatagramTransport
from typing import Any


class UdpProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.packet_queue = asyncio.Queue()
        self._error: Exception|None = None
        
    def connection_made(self, transport: DatagramTransport) -> None:
        pass
    
    def connection_lost(self, exc: Exception|None) -> None:
        pass
    
    def datagram_received(self, data: bytes, addr: tuple[str|Any, int]) -> None:
        self.packet_queue.put_nowait(data)
        
    def error_received(self, exc: Exception) -> None:
        self._error = exc
        self.packet_queue.put_nowait(None)
        
    def raise_if_error(self) -> None:
        if self._error is None:
            # All good.
            pass
        else:
            error = self._error
            self._error = None
            
            raise error
    