
class HttpResponseBody:
    # Body constants.
    BODY_EMPTY_STRING = ""
    
    # Encoding constants.
    ENCODING_BODY = 'utf-8'
    
    
    def __init__(self, http_response_body_string: str):
        self._http_response_body_string: str = http_response_body_string
    
    
    @classmethod
    def create_empty(cls) -> HttpResponseBody:
        return HttpResponseBody(cls.BODY_EMPTY_STRING)
    
    
    @classmethod
    def create_from_bytes(cls, http_response_body_bytes: bytes) -> HttpResponseBody:
        return HttpResponseBody(http_response_body_bytes.decode(cls.ENCODING_BODY))


    def get_http_response_body_string(self) -> str:
        return self._http_response_body_string
    
    
    def get_http_response_body_bytes(self) -> bytes:
        return self._http_response_body_string.encode(self.ENCODING_BODY)
    