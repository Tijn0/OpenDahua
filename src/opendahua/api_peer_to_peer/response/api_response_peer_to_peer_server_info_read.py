from dataclasses import dataclass

from opendahua.api.api_response import ApiResponse
from opendahua.api_peer_to_peer.response.api_response_peer_to_peer import ApiResponsePeerToPeer
from opendahua.object.address import Address


@dataclass(frozen=True)
class ApiResponsePeerToPeerServerInfoRead(ApiResponsePeerToPeer):
    _address_server_upstream: Address
    
    # Field constants.
    FIELD_ADDRESS_SERVER_UPSTREAM = "US"
    
    @classmethod
    def parse(cls, value: dict) -> ApiResponse:
        address_server_upstream = Address(value[cls.FIELD_ADDRESS_SERVER_UPSTREAM])
        
        return cls(address_server_upstream)

    def get_address_server_upstream(self) -> Address:
        return self._address_server_upstream
