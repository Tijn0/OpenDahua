import asyncio
from asyncio import DatagramTransport

from src.helpers import UDP
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
            remote_addr=(address_remote.get_ip(), address_remote.get_port()),
            local_addr=(cls.IP_WILDCARD, port_local),
        )
        
        return cls(transport, protocol, address_remote)
    
    
    @classmethod
    async def create_from_socket(cls, socket: UDP) -> UdpSocket:
        loop = asyncio.get_running_loop()
        
        address_remote = Address.create_from_ip_and_port(socket.rhost, socket.rport)
        
        protocol = UdpProtocol()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: protocol,
            sock=socket,
        )
        
        return cls(transport, protocol, address_remote)


    def send(self, data: bytes) -> None:
        self._transport.sendto(data, addr=(self._address_remote.get_ip(), self._address_remote.get_port()))

    
    async def receive(self) -> bytes:
        data = await self._protocol.queue_receive.get()
        self._protocol.raise_if_error()
        
        if data is None:
            raise UdpSocketClosedError()
        else:
            return data
