from typing import Type

from opendahua.api.api_request import T
from opendahua.api_peer_to_peer.request.api_request_peer_to_peer import ApiRequestPeerToPeer
from opendahua.api_peer_to_peer.response.api_response_peer_to_peer_device_read import ApiResponsePeerToPeerDeviceRead
from opendahua.dahua.dahua_device import DahuaDevice
from opendahua.http.http_request_body import HttpRequestBody
from opendahua.http.http_request_method import HttpRequestMethod
from opendahua.object.url import Url


class ApiRequestPeerToPeerDeviceRead(ApiRequestPeerToPeer[ApiResponsePeerToPeerDeviceRead]):
    # Request constants.
    REQUEST_ENDPOINT = "/info/device/{serial_number}"
    
    def __init__(self, device: DahuaDevice) -> None:
        self._device: DahuaDevice = device
        
    
    def determine_endpoint(self) -> Url:
        return Url(self.REQUEST_ENDPOINT.format(serial_number=self._device.get_serial_number()))
    
    
    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.GET
    
    
    def determine_body_or_none(self) -> HttpRequestBody | None:
        return None
    
    
    def get_response_class(self) -> Type[T]:
        return ApiResponsePeerToPeerDeviceRead
