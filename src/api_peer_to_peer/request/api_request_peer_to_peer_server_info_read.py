from typing import Type

from src.api.api_request import T
from src.api_peer_to_peer.request.api_request_peer_to_peer import ApiRequestPeerToPeer
from src.api_peer_to_peer.response.api_response_peer_to_peer_server_info_read import ApiResponsePeerToPeerServerInfoRead
from src.dahua.dahua_device import DahuaDevice
from src.http.http_request_body import HttpRequestBody
from src.http.http_request_method import HttpRequestMethod
from src.object.url import Url


class ApiRequestPeerToPeerServerInfoRead(ApiRequestPeerToPeer[ApiResponsePeerToPeerServerInfoRead]):
    # Request constants.
    REQUEST_ENDPOINT = "/online/p2psrv/{serial_number}"
    
    def __init__(self, device: DahuaDevice):
        self._device: DahuaDevice = device
        
        
    def determine_endpoint(self) -> Url:
        return Url(
            self.REQUEST_ENDPOINT.format(serial_number=self._device.get_serial_number()),
        )
    
    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.GET
    
    def determine_body_or_none(self) -> HttpRequestBody | None:
        return None
    
    def get_response_class(self) -> Type[T]:
        return ApiResponsePeerToPeerServerInfoRead
