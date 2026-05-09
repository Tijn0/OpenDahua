from src.http.http_request import HttpRequest
from src.http.http_response import HttpResponse
from src.http.http_response_parser import HttpResponseParser
from src.ptcp.ptcp_socket import PtcpSocket


class PtcpHttpClient:
    # Port constants.
    PORT_HTTP = 80
    
    def __init__(self, ptcp_socket: PtcpSocket):
        self._ptcp_socket: PtcpSocket = ptcp_socket
        
        
    async def send_request_and_receive_response(self, request: HttpRequest) -> HttpResponse:
        self._ptcp_socket.send_bind(self.PORT_HTTP)
        
        self._ptcp_socket.send(request.generate_http_request_bytes())
       
        response_bytes = await self._receive_response_bytes()
        
        return HttpResponseParser.parse(response_bytes)
        
        
    async def _receive_response_bytes(self) -> bytes:
        response_bytes = b""
        is_response_complete = False
        
        while not is_response_complete:
            response_chunk = await self._ptcp_socket.receive()
            response_bytes += response_chunk
            
            if HttpResponseParser.is_complete(response_bytes):
                is_response_complete = True
            else:
                # Response is not complete yet.
                pass

        return response_bytes
    