from src.api_peer_to_peer.api_client_peer_to_peer import ApiClientPeerToPeer
from src.api_peer_to_peer.request.api_request_peer_to_peer_device_probe import ApiRequestPeerToPeerDeviceProbe
from src.api_peer_to_peer.request.api_request_peer_to_peer_device_read import ApiRequestPeerToPeerDeviceRead
from src.api_peer_to_peer.request.api_request_peer_to_peer_server_info_read import ApiRequestPeerToPeerServerInfoRead
from src.api_peer_to_peer.request.api_request_peer_to_peer_server_probe import ApiRequestPeerToPeerServerProbe
from src.dahua.dahua_device import DahuaDevice
from src.dahua.dahua_peer_to_peer_connection_error import DahuaPeerToPeerConnectionError
from src.helpers import UDP, get_dec, get_auth, get_key, get_enc
from src.logger import Logger
from src.object.address import Address
from src.object.authentication_identifier import AuthenticationIdentifier
from src.object.cookie import Cookie
from src.object.transaction_identifier import TransactionIdentifier
from src.ptcp.ptcp_socket import PtcpSocket
from src.udp.udp_socket import UdpSocket


class SignalingClient:
    # Error constants.
    ERROR_NO_RESPONSE_FROM_DEVICE = "Timeout occurred while waiting for a response from the device. You are most likely on a symmetric NAT causing the UDP hole punch to fail. This can be fixed by implementing relay mode."
    
    # Main remote constants.
    MAIN_REMOTE_HOST = "www.easy4ipcloud.com"
    MAIN_REMOTE_PORT = 8800
    
    # Endpoint constants.
    ENDPOINT_PEER_TO_PEER_SERVER_PROBE = "/probe/p2psrv"
    ENDPOINT_DEVICE_PEER_TO_PEER_CHANNEL = "/device/{serial_number}/p2p-channel"
    
    # Field constants.
    FIELD_DATA = "data"
    FIELD_BODY = "body"
    FIELD_ADDRESS_SERVER_PEER_TO_PEER = "US"
    FIELD_ADDRESS_DEVICE_LOCAL_ENCRYPTED = "LocalAddr"
    FIELD_ADDRESS_DEVICE_PUBLIC = "PubAddr"
    FIELD_NONCE = "Nonce"
    
    # IP constants.
    IP_LOOPBACK = "127.0.0.1"
    
    # Part constants.
    PART_BODY_ADDRESS_LOCAL_ENCRYPTED = "<IpEncrptV2>true</IpEncrptV2><LocalAddr>{address_local_encrypted}</LocalAddr>"
    
    # Body constants.
    BODY_DEVICE_PEER_TO_PEER_CHANNEL = "<body>{header_authentication}<Identify>{authentication_identifier}</Identify>{part_body_address_local_encrypted}<version>5.0.0</version></body>"
    
    # Separator constants.
    SEPARATOR_ADDRESS = ":"
    
    # Index constants.
    INDEX_ALL_ADDRESS_DEVICE = 1
    INDEX_ADDRESS_DEVICE = 1
    INDEX_PORT_DEVICE = 1
    INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_START = 8
    INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_END = 20
    
    # Number constants.
    NUMBER_OF_PACKET_HANDSHAKE = 4
    NUMBER_OF_ATTEMPT_CONNECTION = 3

    # Time constants.
    TIME_NUMBER_OF_SECOND_TIMEOUT_HANDSHAKE = 1
    TIME_CONNECTION_ATTEMPT_INTERVAL = 5

    # Logging constants.
    LOGGING_CONNECTION_ATTEMPT_FAILED = "Connection attempt with device failed."

    def __init__(self, device: DahuaDevice):
        self._device = device
        
        self._authentication_identifier: AuthenticationIdentifier = AuthenticationIdentifier.create_random()
        self._authentication_key: bytes = get_key(self._device.get_username(), self._device.get_password())
        self._authentication_nonce: int = -1
        
        self._remote_main: UDP = UDP(self.MAIN_REMOTE_HOST, self.MAIN_REMOTE_PORT)
        self._udp_socket_main: UdpSocket|None = None
        
        self._client = ApiClientPeerToPeer()
        
        # TODO: dit misschien op een betere plek neerzetten
        self._address_device_local: Address|None = None
        
        # TODO: ergens alle sockets closen.

    async def connect(self) -> PtcpSocket:
        self._udp_socket_main = await UdpSocket.create_from_socket(self._remote_main)
        await self._probe()
        await self._probe_device()
        
        number_of_attempt_current = 0
        
        while number_of_attempt_current <= self.NUMBER_OF_ATTEMPT_CONNECTION:
            try:
                remote_device: UDP = self._perform_udp_hole_punch()
                
                return await self._perform_ptcp_handshake(remote_device)
            # TODO: Dit specifieker afvangen
            except Exception:
                number_of_attempt_current += 1
                Logger.warning(self.LOGGING_CONNECTION_ATTEMPT_FAILED)
                
        raise DahuaPeerToPeerConnectionError()


    async def _probe(self) -> None:
        await self._client.send_request(ApiRequestPeerToPeerServerProbe(), self._udp_socket_main)
        # self._remote_main.request(self.ENDPOINT_PEER_TO_PEER_SERVER_PROBE)
        
        
    async def _probe_device(self) -> None:
        # TODO: Error als device niet bestaat.
        udp_socket_peer_to_peer = await self._determine_remote_peer_to_peer()
        
        api_request_probe_device = ApiRequestPeerToPeerDeviceProbe(self._device)
        await self._client.send_request(api_request_probe_device, udp_socket_peer_to_peer)
        
        # TODO: random salt shit
        request_device_read = ApiRequestPeerToPeerDeviceRead(self._device)
        await self._client.send_request(request_device_read, udp_socket_peer_to_peer)
        
    
    async def _determine_remote_peer_to_peer(self) -> UdpSocket:
        response = await self._client.send_request(
            ApiRequestPeerToPeerServerInfoRead(self._device),
            self._udp_socket_main,
        )
        
        address_server_peer_to_peer = response.get_address_server_upstream()
        
        return await UdpSocket.create(address_server_peer_to_peer)
    
    
    def _perform_udp_hole_punch(self) -> UDP:
        # We set the remote device connection to the host server first.
        # We use this connection to open up a NAT mapping by making a request to the peer-to-peer server.
        # Then we reuse the connection to perform a UDP hole punch with our peer netting us a connection.
        remote_device = UDP(self._remote_main.rhost, self._remote_main.rport)
        
        header_authentication = self._generate_header_authentication(remote_device.lport)
        
        address_local_encrypted = self._generate_address_local_encrypted(remote_device.lport)
        part_body_address_local_encrypted = self.PART_BODY_ADDRESS_LOCAL_ENCRYPTED.format(
            address_local_encrypted=address_local_encrypted)
        
        body = self.BODY_DEVICE_PEER_TO_PEER_CHANNEL.format(
            header_authentication=header_authentication,
            authentication_identifier=self._authentication_identifier.get_authentication_identifier_string(),
            part_body_address_local_encrypted=part_body_address_local_encrypted,
        )
        
        _ = remote_device.request(
            path=self.ENDPOINT_DEVICE_PEER_TO_PEER_CHANNEL.format(serial_number=self._device.get_serial_number()),
            body=body,
            should_read=False,
        )
        try:
            response = remote_device.read_data(return_error=True, timeout=5)
        except TimeoutError:
            _ = remote_device.request(
                path=self.ENDPOINT_DEVICE_PEER_TO_PEER_CHANNEL.format(serial_number=self._device.get_serial_number()),
                body=body,
                should_read=False,
            )
            response = remote_device.read_data(return_error=True, timeout=5)
        
        address_device_local_encrypted = response[self.FIELD_DATA][self.FIELD_BODY][self.FIELD_ADDRESS_DEVICE_LOCAL_ENCRYPTED]
        self._authentication_nonce = response[self.FIELD_DATA][self.FIELD_BODY][self.FIELD_NONCE]
        address_device_local_string = get_dec(self._authentication_key, self._authentication_nonce, address_device_local_encrypted)
        ip_device_local = address_device_local_string.split(self.SEPARATOR_ADDRESS)[self.INDEX_ALL_ADDRESS_DEVICE][self.INDEX_ADDRESS_DEVICE]
        port_device_local = int(address_device_local_string.split(self.SEPARATOR_ADDRESS)[self.INDEX_PORT_DEVICE])
        
        self._address_device_local = Address.create_from_ip_and_port(ip_device_local, port_device_local)
        
        address_device_public = Address(response[self.FIELD_DATA][self.FIELD_BODY][self.FIELD_ADDRESS_DEVICE_PUBLIC])
        
        remote_device.set_ip(address_device_public.get_ip())
        remote_device.set_port(address_device_public.get_port())
        
        return remote_device
    
    
    async def _perform_ptcp_handshake(self, remote_device: UDP) -> PtcpSocket:
        address_device = Address.create_from_ip_and_port(remote_device.rhost, remote_device.rport)
        cookie = Cookie.create_random()
        
        remote_device.send((
                b"\xff\xfe\xff\xe7"
                + cookie.get_cookie_bytes()
                + TransactionIdentifier.create_random().get_transaction_identifier_bytes()
                + b"\x7f\xd5\xff\xf7"
                + self._authentication_identifier.get_authentication_identifier_bytes_inverted()
                + b"\xff\xfb\xff\xf7\xff\xfe"
                + address_device.get_address_encoded()
        ))
        
        try:
            data = remote_device.recv(timeout=5)
        except TimeoutError:
            raise Exception(self.ERROR_NO_RESPONSE_FROM_DEVICE)
        
        transaction_identifier_response = TransactionIdentifier(data[self.INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_START:self.INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_END])
        remote_device.send((
                b"\xfe\xfe\xff\xe7"
                + cookie.get_cookie_bytes()
                + transaction_identifier_response.get_transaction_identifier_bytes()
                + b"\x7f\xd6\xff\xf7"
                + self._authentication_identifier.get_authentication_identifier_bytes_inverted()
                + b"\xff\xfb\xff\xf7\xff\xfe"
                + self._address_device_local.get_address_encoded()
        ))
        _ = remote_device.recv()
        
        for _ in range(self.NUMBER_OF_PACKET_HANDSHAKE):
            remote_device.send((
                    b"\xfe\xfe\xff\xf3"
                    + cookie.get_cookie_bytes()
                    + transaction_identifier_response.get_transaction_identifier_bytes()
                    + b"\x7f\xd6\xff\xf7"
                    + self._authentication_identifier.get_authentication_identifier_bytes_inverted()
                    + b"\xff\xfb\xff\xf7\xff\xfe"
                    + b"\xa8\x13\x3f\x57\xfe\x37"
            
            ))
            
            remote_device.recv(timeout=self.TIME_NUMBER_OF_SECOND_TIMEOUT_HANDSHAKE)
        
        udp_socket = await UdpSocket.create_from_socket(remote_device)
        
        return PtcpSocket(udp_socket)
        
    
    # TODO: Custom type van maken
    def _generate_header_authentication(self, port_local: int) -> str:
        payload = self._generate_address_local_encrypted(port_local)
        
        return get_auth(
            username=self._device.get_username(),
            key=self._authentication_key,
            nonce=self._authentication_nonce,
            payload=payload,
        )
    
    
    def _generate_address_local_encrypted(self, port_local: int) -> str:
        address_local = Address.create_from_ip_and_port(self.IP_LOOPBACK, port_local)
        
        return get_enc(self._authentication_key, self._authentication_nonce, address_local.get_address_string())
