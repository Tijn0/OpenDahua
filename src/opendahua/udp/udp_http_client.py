from opendahua.http.http_request import HttpRequest
from opendahua.http.http_response import HttpResponse
from opendahua.http.http_response_parser import HttpResponseParser
from opendahua.http.http_status_code import HttpStatusCode
from opendahua.logger import Logger
from opendahua.udp.udp_socket import UdpSocket


class UdpHttpClient:
    # Timeout constants.
    TIMEOUT_NUMBER_OF_SECOND = 30
    
    def __init__(self, udp_socket: UdpSocket):
        self._udp_socket: UdpSocket = udp_socket
        
        
    async def send_request(self, request: HttpRequest) -> HttpResponse:
        self._udp_socket.send(request.generate_http_request_bytes())
        
        Logger.info(request.generate_http_request_bytes())
        
        response = await self._receive_response()
        
        Logger.info(str(response))

        if response.get_status_code() == HttpStatusCode.CONTINUE:
            response = await self._receive_response()
            
            Logger.info(str(response))
        else:
            # Got response.
            pass
            
        return response
    
        
    async def _receive_response(self) -> HttpResponse:
        response_parser = HttpResponseParser()
        
        while not response_parser.is_complete():
            response_chunk = await self._udp_socket.receive(self.TIMEOUT_NUMBER_OF_SECOND)
            
            response_parser.feed(response_chunk)
        
        return response_parser.build()
