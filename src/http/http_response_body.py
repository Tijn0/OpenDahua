
class HttpResponseBody:
    # Body constants.
    BODY_EMPTY= b""
    
    # Encoding constants.
    ENCODING_BODY = 'utf-8'
    
    def __init__(self, http_response_body_bytes: bytes):
        self._http_response_body_bytes: bytes = http_response_body_bytes
    
    
    @classmethod
    def create_empty(cls) -> HttpResponseBody:
        return HttpResponseBody(cls.BODY_EMPTY)
    
    
    def get_http_response_body_string(self) -> str:
        return self._http_response_body_bytes.decode(self.ENCODING_BODY)
    
    
    def get_http_response_body_bytes(self) -> bytes:
        return self._http_response_body_bytes
    