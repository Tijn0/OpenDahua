from opendahua.api_peer_to_peer.api_client_peer_to_peer import ApiClientPeerToPeer
from opendahua.api_peer_to_peer.api_peer_to_peer_authentication_util import ApiPeerToPeerAuthenticationUtil
from opendahua.api_peer_to_peer.object.api_peer_to_peer_random_salt import ApiPeerToPeerRandomSalt
from opendahua.api_peer_to_peer.request.api_peer_to_peer_encryption_util import ApiPeerToPeerEncryptionUtil
from opendahua.api_peer_to_peer.request.api_request_peer_to_peer_channel_create import ApiRequestPeerToPeerChannelCreate
from opendahua.api_peer_to_peer.request.api_request_peer_to_peer_device_probe import ApiRequestPeerToPeerDeviceProbe
from opendahua.api_peer_to_peer.request.api_request_peer_to_peer_device_read import ApiRequestPeerToPeerDeviceRead
from opendahua.api_peer_to_peer.request.api_request_peer_to_peer_server_info_read import ApiRequestPeerToPeerServerInfoRead
from opendahua.api_peer_to_peer.request.api_request_peer_to_peer_server_probe import ApiRequestPeerToPeerServerProbe
from opendahua.common_object.nonce import Nonce
from opendahua.dahua.dahua_device import DahuaDevice
from opendahua.dahua.dahua_peer_to_peer_connection_error import DahuaPeerToPeerConnectionError
from opendahua.logger import Logger
from opendahua.object.address import Address
from opendahua.object.authentication_identifier import AuthenticationIdentifier
from opendahua.object.cookie import Cookie
from opendahua.object.transaction_identifier import TransactionIdentifier
from opendahua.ptcp.ptcp_socket import PtcpSocket
from opendahua.udp.udp_socket import UdpSocket


class SignalingClient:
    # Error constants.
    ERROR_NO_RESPONSE_FROM_DEVICE = "Timeout occurred while waiting for a response from the device. You are most likely on a symmetric NAT causing the UDP hole punch to fail. This can be fixed by implementing relay mode."
    ERROR_UNEXPECTED = "Unexpected exception."
    
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
    NUMBER_OF_ATTEMPT_CONNECTION_MAXIMUM = 3

    # Time constants.
    TIME_NUMBER_OF_SECOND_TIMEOUT_HANDSHAKE = 1
    TIME_CONNECTION_ATTEMPT_INTERVAL = 5
    
    # Separator constants.
    SEPARATOR_IP = ","
    SEPARATOR_IP_PORT = ":"

    # Logging constants.
    LOGGING_CONNECTION_ATTEMPT_FAILED = "Connection attempt with device failed. ({number_of_attempt_current}/{number_of_attempt_maximum})"

    def __init__(self, device: DahuaDevice) -> None:
        self._device = device
        
        self._client = ApiClientPeerToPeer()
        self._authentication_identifier: AuthenticationIdentifier = AuthenticationIdentifier.create_random()
        

    async def connect(self) -> PtcpSocket:
        udp_socket_main = await self._probe()
        random_salt = await self._determine_random_salt(udp_socket_main)
        udp_socket_main.close()
        
        return await self.determine_ptcp_socket_device(random_salt)

    async def _probe(self) -> UdpSocket:
        udp_socket_main = await UdpSocket.create(
            Address.create_from_ip_and_port(self.MAIN_REMOTE_HOST, self.MAIN_REMOTE_PORT),
        )
        await self._client.send_request(ApiRequestPeerToPeerServerProbe(), udp_socket_main)
        
        return udp_socket_main

        
    async def _determine_random_salt(self, udp_socket_main: UdpSocket) -> ApiPeerToPeerRandomSalt:
        # TODO: Error als device niet bestaat.
        udp_socket_peer_to_peer = await self._determine_remote_peer_to_peer(udp_socket_main)
        
        api_request_probe_device = ApiRequestPeerToPeerDeviceProbe(self._device)
        await self._client.send_request(api_request_probe_device, udp_socket_peer_to_peer)
        
        request_device_read = ApiRequestPeerToPeerDeviceRead(self._device)
        response_device_read = await self._client.send_request(request_device_read, udp_socket_peer_to_peer)
        
        udp_socket_peer_to_peer.close()
        
        return response_device_read.get_random_salt()
    
    
    async def _determine_remote_peer_to_peer(self, udp_socket_main: UdpSocket) -> UdpSocket:
        response = await self._client.send_request(
            ApiRequestPeerToPeerServerInfoRead(self._device),
            udp_socket_main,
        )
        
        address_server_peer_to_peer = response.get_address_server_upstream()
        
        return await UdpSocket.create(address_server_peer_to_peer)
    
    
    async def determine_ptcp_socket_device(self, random_salt: ApiPeerToPeerRandomSalt) -> PtcpSocket:
        for number_of_attempt_current in range(1, self.NUMBER_OF_ATTEMPT_CONNECTION_MAXIMUM + 1):
            try:
                udp_socket_device, address_local_device = await self._determine_udp_socket_device(random_salt)
                
                return await self._determine_ptcp_socket_device(udp_socket_device, address_local_device)
            except DahuaPeerToPeerConnectionError:
                Logger.warning(
                    self.LOGGING_CONNECTION_ATTEMPT_FAILED.format(
                        number_of_attempt_current=number_of_attempt_current,
                        number_of_attempt_maximum=self.NUMBER_OF_ATTEMPT_CONNECTION_MAXIMUM,
                    ),
                )
                
                if number_of_attempt_current == self.NUMBER_OF_ATTEMPT_CONNECTION_MAXIMUM:
                    raise
            
        raise Exception(self.ERROR_UNEXPECTED)
    
    
    async def _determine_udp_socket_device(self, random_salt: ApiPeerToPeerRandomSalt) -> tuple[UdpSocket, Address]:
        # We set the remote device connection to the host server first.
        # We use this connection to open up a NAT mapping by making a request to the peer-to-peer server.
        # Then we reuse the connection to perform a UDP hole punch with our peer netting us a connection.
        address_main = Address.create_from_ip_and_port(self.MAIN_REMOTE_HOST, self.MAIN_REMOTE_PORT)

        udp_socket_device = await UdpSocket.create(address_main)
        
        key_authentication = ApiPeerToPeerAuthenticationUtil.generate_key_authentication(self._device, random_salt)
        
        address_local = Address.create_from_ip_and_port(self.IP_LOOPBACK, udp_socket_device.get_address_local().get_port())
        request_peer_to_peer_channel_create = ApiRequestPeerToPeerChannelCreate(
            device=self._device,
            address_local=address_local,
            authentication_identifier=self._authentication_identifier,
            nonce=Nonce.create_random(),
            random_salt=random_salt,
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
            
            address_device_local = Address.create_from_ip_and_port(all_ip[self.INDEX_LAST], int(port_string))
        else:
            address_device_local = Address(address_device_local_string)
        
        address_device_public = response_peer_to_peer_channel_create.get_address_device_public()
        
        udp_socket_device.set_address_remote(address_device_public)
        
        return udp_socket_device, address_device_local
    
    
    async def _determine_ptcp_socket_device(
            self,
            udp_socket_device: UdpSocket,
            address_device_local: Address,
    ) -> PtcpSocket:
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
            data = await udp_socket_device.receive(self.TIME_NUMBER_OF_SECOND_TIMEOUT_HANDSHAKE)
        except TimeoutError:
            raise DahuaPeerToPeerConnectionError(self.ERROR_NO_RESPONSE_FROM_DEVICE)

        transaction_identifier_response = TransactionIdentifier(data[self.INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_START:self.INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_END])
        udp_socket_device.send((
                b"\xfe\xfe\xff\xe7"
                + cookie.get_cookie_bytes()
                + transaction_identifier_response.get_transaction_identifier_bytes()
                + b"\x7f\xd6\xff\xf7"
                + self._authentication_identifier.get_authentication_identifier_bytes_inverted()
                + b"\xff\xfb\xff\xf7\xff\xfe"
                + address_device_local.get_address_encoded()
        ))
        await udp_socket_device.receive(timeout=self.TIME_NUMBER_OF_SECOND_TIMEOUT_HANDSHAKE)

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
            await udp_socket_device.receive(timeout=self.TIME_NUMBER_OF_SECOND_TIMEOUT_HANDSHAKE)
            
        return PtcpSocket(udp_socket_device)
