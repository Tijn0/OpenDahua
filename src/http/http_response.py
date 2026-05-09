from src.http.http_header import HttpHeader
from src.http.http_response_body import HttpResponseBody
from src.http.http_status_code import HttpStatusCode


class HttpResponse:
    def __init__(self, status_code: HttpStatusCode, all_header: list[HttpHeader], body: HttpResponseBody|None):
        self._status_code: HttpStatusCode = status_code
        self._all_header: list[HttpHeader] = all_header
        self._body: HttpResponseBody|None = body
    
    
    def get_status_code(self) -> HttpStatusCode:
        return self._status_code
    
    
    def get_all_header(self) -> list[HttpHeader]:
        return self._all_header
    
    
    def get_body_or_none(self) -> HttpResponseBody|None:
        return self._body
    
        