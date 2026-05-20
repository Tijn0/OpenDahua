from src.http.http_header import HttpHeader
from src.http.http_response_body import HttpResponseBody
from src.http.http_status_code import HttpStatusCode


class HttpResponse:
    # Format constants.
    FORMAT_HTTP_RESPONSE_STRING = (
        "HttpResponse("
        "status_code={status_code}, "
        "headers={headers}, "
        "body={body}"
        ")"
    )
    
    def __init__(self, status_code: HttpStatusCode, all_header: list[HttpHeader], body: HttpResponseBody):
        self._status_code: HttpStatusCode = status_code
        self._all_header: list[HttpHeader] = all_header
        self._body: HttpResponseBody = body
    
    
    def get_status_code(self) -> HttpStatusCode:
        return self._status_code
    
    
    def get_all_header(self) -> list[HttpHeader]:
        return self._all_header
    
    
    def get_body(self) -> HttpResponseBody:
        return self._body
    
    
    def get_header_or_none(self, key: str) -> HttpHeader|None:
        # TODO: hashmap
        for header in self._all_header:
            if header.get_header_key_string() == key:
                return header
            else:
                # Keep looking.
                pass
        
        return None
        
        
    def __str__(self) -> str:
        return self.FORMAT_HTTP_RESPONSE_STRING.format(
            status_code=self._status_code,
            headers=self._all_header,
            body=self._body,
        )
