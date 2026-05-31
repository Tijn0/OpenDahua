from opendahua.http.http_header import HttpHeader
from opendahua.http.http_request_body import HttpRequestBody
from opendahua.http.http_request_method import HttpRequestMethod
from opendahua.object.url import Url


class HttpRequest:
    # Http constants.
    HTTP_PROTOCOL = "HTTP/1.1"

    # Header constants.
    HEADER_KEY_CONTENT_LENGTH = "Content-Length"
    HEADER_KEY_HOST = "Host"

    # Format constants.
    FORMAT_REQUEST_LINE = "{method} {url} {protocol}\r\n"
    
    # Character constants.
    CHARACTER_CRLF = "\r\n"
    
    # Encoding constants.
    ENCODING_BODY = "utf-8"
    ENCODING_REQUEST = "ascii"

    # String constants.
    STRING_EMPTY = ""

    def __init__(self,
                 method: HttpRequestMethod,
                 url: Url,
                 all_header: list[HttpHeader]|None = None,
                 body: HttpRequestBody|None = None):
        if all_header is None:
            all_header = []
        else:
            # Headers already set.
            pass
        
        self._method: HttpRequestMethod = method
        self._url: Url = url
        self._body: HttpRequestBody|None = body
        self._all_header: list[HttpHeader] = all_header
        
        
    def generate_http_request_bytes(self) -> bytes:
        request_line_string = self._generate_request_line_string()
        all_header_string = self._generate_all_header_string()
        
        request_string = request_line_string + all_header_string + self.CHARACTER_CRLF
        
        request_bytes = request_string.encode(self.ENCODING_REQUEST)
        body_bytes = self.determine_body_bytes()
        
        return request_bytes + body_bytes
        
        
    def _generate_request_line_string(self) -> str:
        return self.FORMAT_REQUEST_LINE.format(
            method=self._method.value,
            url=self._url.get_url_string(), # TODO: Base weghalen maar query parameters behouden.
            protocol=self.HTTP_PROTOCOL,
        )
    

    def _generate_all_header_string(self) -> str:
        all_header = self._all_header.copy()
        all_header = self._add_header_content_length_if_needed(all_header)
        all_header = self._add_header_host_if_needed(all_header)

        all_header_string = self.STRING_EMPTY
        
        for header in all_header:
            all_header_string += header.get_http_header_string() + self.CHARACTER_CRLF
        
        return all_header_string
        
        
    def _add_header_content_length_if_needed(self, all_header: list[HttpHeader]) -> list[HttpHeader]:
        body = self._body
        
        if body is None:
            # Request doesn't have a body so don't add the content-length header.
            return all_header
        else:
            byte_size_body = len(body.get_http_request_body_string().encode(self.ENCODING_BODY))
            
            all_header.append(HttpHeader(self.HEADER_KEY_CONTENT_LENGTH, str(byte_size_body)))
            
            return all_header
    
    
    def _add_header_host_if_needed(self, all_header: list[HttpHeader]) -> list[HttpHeader]:
        host = self._url.get_host_string_or_none()
        
        if host is None:
            # Request url doesn't have a host part so we don't add the host header.
            return all_header
        else:
            all_header.append(HttpHeader(self.HEADER_KEY_HOST, host))
            
            return all_header
    
    
    def determine_body_bytes(self) -> bytes:
        body = self._body
        
        if body is None:
            return HttpRequestBody.create_empty().get_http_request_body_bytes()
        else:
            return body.get_http_request_body_bytes()
        
        
    def add_header(self, header: HttpHeader) -> None:
        self._all_header.append(header)
        
        
    def get_url(self) -> Url:
        return self._url
    
    
    def get_method(self) -> HttpRequestMethod:
        return self._method
