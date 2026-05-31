from typing import TypeVar, Generic

from opendahua.api.api_request import ApiRequest
from opendahua.api_peer_to_peer.response.api_response_peer_to_peer import ApiResponsePeerToPeer

T = TypeVar("T", bound=ApiResponsePeerToPeer)

class ApiRequestPeerToPeer(ApiRequest[T], Generic[T]):
    pass
