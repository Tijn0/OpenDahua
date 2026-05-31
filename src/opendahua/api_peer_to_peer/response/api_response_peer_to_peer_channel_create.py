from dataclasses import dataclass

from opendahua.api.api_response import ApiResponse
from opendahua.api_peer_to_peer.response.api_response_peer_to_peer import ApiResponsePeerToPeer
from opendahua.common_object.nonce import Nonce
from opendahua.object.address import Address


@dataclass(frozen=True)
class ApiResponsePeerToPeerChannelCreate(ApiResponsePeerToPeer):
    _address_device_local_encrypted: str
    _address_device_public: Address
    _nonce: Nonce
    
    # Field constants.
    FIELD_ADDRESS_LOCAL_ENCRYPTED = "LocalAddr"
    FIELD_ADDRESS_PUBLIC = "PubAddr"
    FIELD_NONCE = "Nonce"

    @classmethod
    def parse(cls, value: dict) -> ApiResponse:
        address_device_local_encrypted = value[cls.FIELD_ADDRESS_LOCAL_ENCRYPTED]
        address_device_public = Address(value[cls.FIELD_ADDRESS_PUBLIC])
        nonce = Nonce(value[cls.FIELD_NONCE])
        
        return cls(address_device_local_encrypted, address_device_public, nonce)
        
        
    def get_address_device_local_encrypted(self) -> str:
        return self._address_device_local_encrypted


    def get_nonce(self) -> Nonce:
        return self._nonce


    def get_address_device_public(self) -> Address:
        return self._address_device_public
