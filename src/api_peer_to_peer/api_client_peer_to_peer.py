import xmltodict

from src.api.api_request import T
from src.api_peer_to_peer.api_peer_to_peer_authentication_util import ApiPeerToPeerAuthenticationUtil
from src.api_peer_to_peer.api_peer_to_peer_body_parser import ApiPeerToPeerBodyParser
from src.api_peer_to_peer.request.api_request_peer_to_peer import ApiRequestPeerToPeer
from src.common_object.dahua_error import DahuaError
from src.http.http_header import HttpHeader
from src.http.http_request import HttpRequest
from src.http.http_response import HttpResponse
from src.http.http_status_code import HttpStatusCode
from src.udp.udp_http_client import UdpHttpClient
from src.udp.udp_socket import UdpSocket


class ApiClientPeerToPeer:
    # Error constants.
    ERROR_PEER_TO_PEER_API = "Received error response from peer to peer API: \"{http_response}\"."
    
    # Header constants.
    HEADER_KEY_SEQUENCE = "CSeq"
    
    # Increment constants.
    INCREMENT_SEQUENCE_NUMBER = 1

    def __init__(self):
        self._sequence_number = 1
    
    
    async def send_request(self, api_request: ApiRequestPeerToPeer[T], udp_socket: UdpSocket) -> T:
        client = UdpHttpClient(udp_socket)
        
        http_request = api_request.generate_http_request()
        http_request = self._add_header_sequence_number(http_request)
        http_request = self._add_all_header_authentication(http_request)
        
        http_response = await client.send_request(http_request)
        
        if self._is_http_response_success(http_response):
            return self._parse_api_response(api_request, http_response)
        else:
            raise DahuaError(self.ERROR_PEER_TO_PEER_API.format(http_response=http_response))
    
    
    def _add_header_sequence_number(self, http_request: HttpRequest) -> HttpRequest:
        http_request.add_header(HttpHeader(self.HEADER_KEY_SEQUENCE, str(self._sequence_number)))
        self._sequence_number += self.INCREMENT_SEQUENCE_NUMBER
        
        return http_request
    
    
    def _add_all_header_authentication(self, http_request: HttpRequest) -> HttpRequest:
        http_request.add_header(ApiPeerToPeerAuthenticationUtil.generate_header_authorization())
        http_request.add_header(ApiPeerToPeerAuthenticationUtil.generate_header_authentication())

        return http_request


    def _is_http_response_success(self, http_response: HttpResponse) -> bool:
        return http_response.get_status_code() in self._get_all_http_status_code_success()
    
    
    @staticmethod
    def _get_all_http_status_code_success() -> list[HttpStatusCode]:
        return [
            HttpStatusCode.OK,
        ]
    
    
    def _parse_api_response(self, api_request: ApiRequestPeerToPeer[T], http_response: HttpResponse) -> T:
        response_class = api_request.get_response_class()
        response_unparsed = ApiPeerToPeerBodyParser.parse(http_response.get_body())
        
        return response_class.parse(response_unparsed)
