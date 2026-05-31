from opendahua.http.http_request import HttpRequest
from opendahua.http.http_response import HttpResponse
from opendahua.http.http_response_parser import HttpResponseParser
from opendahua.logger import Logger
from opendahua.ptcp.ptcp_socket import PtcpSocket


class PtcpHttpClient:
    # Port constants.
    PORT_HTTP = 80
    
    # Response constants.
    RESPONSE_EMPTY = b""
    
    # Timeout constants.
    TIMEOUT_NUMBER_OF_SECOND = 30
    
    def __init__(self, ptcp_socket: PtcpSocket) -> None:
        self._ptcp_socket: PtcpSocket = ptcp_socket
        
        
    async def connect(self) -> None:
        await self._ptcp_socket.connect()
    
    
    async def disconnect(self) -> None:
        await self._ptcp_socket.disconnect()
        

    async def send_request(self, request: HttpRequest) -> HttpResponse:
        self._ptcp_socket.open_port(self.PORT_HTTP)
        
        Logger.info(request.generate_http_request_bytes())
        
        self._ptcp_socket.send(request.generate_http_request_bytes())
        
        response = await self._receive_response()
        
        Logger.info(str(response))
        
        return response
        
        
    async def _receive_response(self) -> HttpResponse:
        response_parser = HttpResponseParser()
        
        while not response_parser.is_complete():
            response_chunk = await self._ptcp_socket.receive(self.TIMEOUT_NUMBER_OF_SECOND)
            
            response_parser.feed(response_chunk)

        return response_parser.build()
    
    
    def get_ptcp_socket(self) -> PtcpSocket:
        return self._ptcp_socket
