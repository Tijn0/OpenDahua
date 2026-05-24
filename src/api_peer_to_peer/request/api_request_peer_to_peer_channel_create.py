from typing import Type

from src.api.api_request import T
from src.api_peer_to_peer.api_peer_to_peer_authentication_util import ApiPeerToPeerAuthenticationUtil
from src.api_peer_to_peer.object.api_peer_to_peer_random_salt import ApiPeerToPeerRandomSalt
from src.api_peer_to_peer.request.api_peer_to_peer_encryption_util import ApiPeerToPeerEncryptionUtil
from src.api_peer_to_peer.request.api_request_peer_to_peer import ApiRequestPeerToPeer
from src.api_peer_to_peer.response.api_response_peer_to_peer_channel_create import ApiResponsePeerToPeerChannelCreate
from src.common_object.key import Key
from src.common_object.nonce import Nonce
from src.dahua.dahua_device import DahuaDevice
from src.http.http_request_body import HttpRequestBody
from src.http.http_request_method import HttpRequestMethod
from src.object.address import Address
from src.object.authentication_identifier import AuthenticationIdentifier
from src.object.url import Url


class ApiRequestPeerToPeerChannelCreate(ApiRequestPeerToPeer[ApiResponsePeerToPeerChannelCreate]):
    # Request constants.
    REQUEST_ENDPOINT = "/device/{serial_number}/p2p-channel"
    
    # Format constants.
    FORMAT_BODY = "<body>{part_body_authentication}<Identify>{authentication_identifier}</Identify><IpEncrptV2>true</IpEncrptV2><LocalAddr>{address_local_encrypted}</LocalAddr><version>5.0.0</version></body>"

    def __init__(
            self,
            device: DahuaDevice,
            address_local: Address,
            authentication_identifier: AuthenticationIdentifier,
            nonce: Nonce,
            random_salt: ApiPeerToPeerRandomSalt,
            key_authentication: Key,
    ):
        self._device: DahuaDevice = device
        self._address_local: Address = address_local
        self._authentication_identifier: AuthenticationIdentifier = authentication_identifier
        self._nonce: Nonce = nonce
        self._random_salt: ApiPeerToPeerRandomSalt = random_salt
        self._key_authentication: Key = key_authentication


    def determine_endpoint(self) -> Url:
        return Url(self.REQUEST_ENDPOINT.format(serial_number=self._device.get_serial_number()))
    
    
    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.POST
    
    
    def determine_body_or_none(self) -> HttpRequestBody | None:
        address_local_encrypted = ApiPeerToPeerEncryptionUtil.encrypt(
            self._key_authentication,
            self._nonce,
            self._address_local.get_address_string(),
        )
        part_body_authentication = ApiPeerToPeerAuthenticationUtil.generate_part_body_authentication(
            device=self._device,
            key_authentication=self._key_authentication,
            payload=address_local_encrypted,
            nonce=self._nonce,
            random_salt=self._random_salt,
        )

        return HttpRequestBody(
            self.FORMAT_BODY.format(
                part_body_authentication=part_body_authentication,
                authentication_identifier=self._authentication_identifier.get_authentication_identifier_string(),
                address_local_encrypted=address_local_encrypted,
            )
        )
    
    
    def get_response_class(self) -> Type[T]:
        return ApiResponsePeerToPeerChannelCreate
