from typing import Type

from src.api.api_request import T
from src.api_peer_to_peer.request.api_request_peer_to_peer import ApiRequestPeerToPeer
from src.api_peer_to_peer.response.api_response_peer_to_peer_server_probe import ApiResponsePeerToPeerServerProbe
from src.http.http_request_body import HttpRequestBody
from src.http.http_request_method import HttpRequestMethod
from src.object.url import Url


class ApiRequestPeerToPeerServerProbe(ApiRequestPeerToPeer[ApiResponsePeerToPeerServerProbe]):
    # Request constants.
    REQUEST_ENDPOINT = "/probe/p2psrv"
    
    def determine_endpoint(self) -> Url:
        return Url(self.REQUEST_ENDPOINT)
    
    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.GET
    
    def determine_body_or_none(self) -> HttpRequestBody | None:
        return None
    
    def get_response_class(self) -> Type[T]:
        return ApiResponsePeerToPeerServerProbe
