from src.api_peer_to_peer.api_client_peer_to_peer import ApiClientPeerToPeer
from src.api_peer_to_peer.api_peer_to_peer_authentication_util import ApiPeerToPeerAuthenticationUtil
from src.api_peer_to_peer.object.api_peer_to_peer_random_salt import ApiPeerToPeerRandomSalt
from src.api_peer_to_peer.request.api_peer_to_peer_encryption_util import ApiPeerToPeerEncryptionUtil
from src.api_peer_to_peer.request.api_request_peer_to_peer_channel_create import ApiRequestPeerToPeerChannelCreate
from src.api_peer_to_peer.request.api_request_peer_to_peer_device_probe import ApiRequestPeerToPeerDeviceProbe
from src.api_peer_to_peer.request.api_request_peer_to_peer_device_read import ApiRequestPeerToPeerDeviceRead
from src.api_peer_to_peer.request.api_request_peer_to_peer_server_info_read import ApiRequestPeerToPeerServerInfoRead
from src.api_peer_to_peer.request.api_request_peer_to_peer_server_probe import ApiRequestPeerToPeerServerProbe
from src.common_object.nonce import Nonce
from src.dahua.dahua_device import DahuaDevice
from src.dahua.dahua_peer_to_peer_connection_error import DahuaPeerToPeerConnectionError
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
    
    # IP constants.
    IP_LOOPBACK = "127.0.0.1"
    
    # Index constants.
    INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_START = 8
    INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_END = 20
    INDEX_LAST = -1
    
    # Number constants.
    NUMBER_OF_PACKET_HANDSHAKE = 4
    NUMBER_OF_ATTEMPT_CONNECTION = 3

    # Time constants.
    TIME_NUMBER_OF_SECOND_TIMEOUT_HANDSHAKE = 1
    TIME_CONNECTION_ATTEMPT_INTERVAL = 5
    
    # Separator constants.
    SEPARATOR_IP = ","
    SEPARATOR_IP_PORT = ":"

    # Logging constants.
    LOGGING_CONNECTION_ATTEMPT_FAILED = "Connection attempt with device failed."

    def __init__(self, device: DahuaDevice):
        self._device = device
        
        self._authentication_identifier: AuthenticationIdentifier = AuthenticationIdentifier.create_random()
        self._udp_socket_main: UdpSocket|None = None
        
        self._client = ApiClientPeerToPeer()
        
        # TODO: dit misschien op een betere plek neerzetten
        self._address_device_local: Address|None = None
        self._random_salt: ApiPeerToPeerRandomSalt|None = None

        # TODO: ergens alle sockets closen.

    async def connect(self) -> PtcpSocket:
        self._udp_socket_main = await UdpSocket.create(
            Address.create_from_ip_and_port(self.MAIN_REMOTE_HOST, self.MAIN_REMOTE_PORT),
        )
        await self._probe()
        await self._probe_device()
        
        number_of_attempt_current = 0
        
        while number_of_attempt_current <= self.NUMBER_OF_ATTEMPT_CONNECTION:
            try:
                remote_device: UdpSocket = await self._perform_udp_hole_punch()
                
                return await self._perform_ptcp_handshake(remote_device)
            # TODO: Dit specifieker afvangen
            except Exception as exception:
                print(exception)
                number_of_attempt_current += 1
                Logger.warning(self.LOGGING_CONNECTION_ATTEMPT_FAILED)
                
        raise DahuaPeerToPeerConnectionError()


    async def _probe(self) -> None:
        await self._client.send_request(ApiRequestPeerToPeerServerProbe(), self._udp_socket_main)
        
        
    async def _probe_device(self) -> None:
        # TODO: Error als device niet bestaat.
        udp_socket_peer_to_peer = await self._determine_remote_peer_to_peer()
        
        api_request_probe_device = ApiRequestPeerToPeerDeviceProbe(self._device)
        await self._client.send_request(api_request_probe_device, udp_socket_peer_to_peer)
        
        # TODO: random salt shit
        request_device_read = ApiRequestPeerToPeerDeviceRead(self._device)
        response_device_read = await self._client.send_request(request_device_read, udp_socket_peer_to_peer)
        
        udp_socket_peer_to_peer.close()
        
        self._random_salt = response_device_read.get_random_salt()
        
    
    async def _determine_remote_peer_to_peer(self) -> UdpSocket:
        response = await self._client.send_request(
            ApiRequestPeerToPeerServerInfoRead(self._device),
            self._udp_socket_main,
        )
        
        address_server_peer_to_peer = response.get_address_server_upstream()
        
        return await UdpSocket.create(address_server_peer_to_peer)
    
    
    async def _perform_udp_hole_punch(self) -> UdpSocket:
        # We set the remote device connection to the host server first.
        # We use this connection to open up a NAT mapping by making a request to the peer-to-peer server.
        # Then we reuse the connection to perform a UDP hole punch with our peer netting us a connection.
        address_main = Address.create_from_ip_and_port(self.MAIN_REMOTE_HOST, self.MAIN_REMOTE_PORT)

        udp_socket_device = await UdpSocket.create(address_main)
        
        key_authentication = ApiPeerToPeerAuthenticationUtil.generate_key_authentication(self._device, self._random_salt)
        
        address_local = Address.create_from_ip_and_port(self.IP_LOOPBACK, udp_socket_device.get_address_local().get_port())
        request_peer_to_peer_channel_create = ApiRequestPeerToPeerChannelCreate(
            device=self._device,
            address_local=address_local,
            authentication_identifier=self._authentication_identifier,
            nonce=Nonce.create_random(),
            random_salt=self._random_salt,
            key_authentication=key_authentication,
        )
        response_peer_to_peer_channel_create = await self._client.send_request(request_peer_to_peer_channel_create, udp_socket_device)
        
        address_device_local_encrypted = response_peer_to_peer_channel_create.get_address_device_local_encrypted()
        nonce = response_peer_to_peer_channel_create.get_nonce()
        address_device_local_string = ApiPeerToPeerEncryptionUtil.decrypt(key_authentication, nonce, address_device_local_encrypted)
        
        if self.SEPARATOR_IP in address_device_local_string:
            # We got multiple IP addresses.
            all_ip_string, _, port_string = address_device_local_string.partition(self.SEPARATOR_IP_PORT)
            all_ip = all_ip_string.split(self.SEPARATOR_IP)
            
            self._address_device_local = Address.create_from_ip_and_port(all_ip[self.INDEX_LAST], int(port_string))
        else:
            self._address_device_local = Address(address_device_local_string)
        
        address_device_public = response_peer_to_peer_channel_create.get_address_device_public()
        
        udp_socket_device.set_address_remote(address_device_public)
        
        return udp_socket_device
    
    
    async def _perform_ptcp_handshake(self, udp_socket_device: UdpSocket) -> PtcpSocket:
        address_device = udp_socket_device.get_address_remote()
        cookie = Cookie.create_random()
        
        udp_socket_device.send((
                b"\xff\xfe\xff\xe7"
                + cookie.get_cookie_bytes()
                + TransactionIdentifier.create_random().get_transaction_identifier_bytes()
                + b"\x7f\xd5\xff\xf7"
                + self._authentication_identifier.get_authentication_identifier_bytes_inverted()
                + b"\xff\xfb\xff\xf7\xff\xfe"
                + address_device.get_address_encoded()
        ))

        try:
            # TODO: Timeout weer laten werken.
            data = await udp_socket_device.receive()
        except TimeoutError:
            raise Exception(self.ERROR_NO_RESPONSE_FROM_DEVICE)

        transaction_identifier_response = TransactionIdentifier(data[self.INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_START:self.INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_END])
        udp_socket_device.send((
                b"\xfe\xfe\xff\xe7"
                + cookie.get_cookie_bytes()
                + transaction_identifier_response.get_transaction_identifier_bytes()
                + b"\x7f\xd6\xff\xf7"
                + self._authentication_identifier.get_authentication_identifier_bytes_inverted()
                + b"\xff\xfb\xff\xf7\xff\xfe"
                + self._address_device_local.get_address_encoded()
        ))
        await udp_socket_device.receive()

        for _ in range(self.NUMBER_OF_PACKET_HANDSHAKE):
            udp_socket_device.send((
                    b"\xfe\xfe\xff\xf3"
                    + cookie.get_cookie_bytes()
                    + transaction_identifier_response.get_transaction_identifier_bytes()
                    + b"\x7f\xd6\xff\xf7"
                    + self._authentication_identifier.get_authentication_identifier_bytes_inverted()
                    + b"\xff\xfb\xff\xf7\xff\xfe"
                    + b"\xa8\x13\x3f\x57\xfe\x37"

            ))
            await udp_socket_device.receive()
            
        return PtcpSocket(udp_socket_device)
