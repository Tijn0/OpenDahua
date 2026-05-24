import asyncio
from asyncio import DatagramTransport

from src.logger import Logger
from src.object.address import Address
from src.udp.udp_protocol import UdpProtocol
from src.udp.udp_socket_closed_error import UdpSocketClosedError


class UdpSocket:
    # Ip constants.
    IP_WILDCARD = "0.0.0.0"
    
    # Port constants.
    PORT_EPHEMERAL = 0
    
    # Index constants.
    INDEX_HOST_LOCAL = 0
    INDEX_PORT_LOCAL = 1
    
    # Logging constants.
    LOGGING_CLOSING = "[UDP] Closing."
    
    # Info constants.
    INFO_SOCKNAME = "sockname"

    
    def __init__(self, transport: DatagramTransport, protocol: UdpProtocol, address_remote: Address):
        self._transport = transport
        self._protocol = protocol
        
        self._address_remote = address_remote
        
        
    @classmethod
    async def create(cls, address_remote: Address, port_local: int = 0) -> UdpSocket:
        loop = asyncio.get_running_loop()
        
        protocol = UdpProtocol()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: protocol,
            local_addr=(cls.IP_WILDCARD, port_local),
        )
        
        return cls(transport, protocol, address_remote)
    

    def send(self, data: bytes) -> None:
        self._transport.sendto(data, addr=(self._address_remote.get_ip(), self._address_remote.get_port()))

    
    async def receive(self, timeout: int|float = None) -> bytes:
        data = await asyncio.wait_for(self._protocol.queue_receive.get(), timeout)
        
        self._protocol.raise_if_error()
        
        if data is None:
            raise UdpSocketClosedError()
        else:
            return data


    def set_address_remote(self, address_remote: Address) -> None:
        self._address_remote = address_remote
        
        
    def get_address_remote(self) -> Address:
        return self._address_remote
    
    
    def get_address_local(self) -> Address:
        ip_local, port_local = self._transport.get_extra_info(self.INFO_SOCKNAME)
        
        return Address.create_from_ip_and_port(ip_local, port_local)
    

    def close(self) -> None:
        Logger.debug(self.LOGGING_CLOSING)
        
        self._transport.close()
