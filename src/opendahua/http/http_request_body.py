

class HttpRequestBody:
    # Body constants.
    BODY_EMPTY_STRING = ""
    
    # Encoding constants.
    ENCODING_BODY = 'utf-8'
    
    
    def __init__(self, http_request_body_string: str):
        self._http_request_body_string: str = http_request_body_string
        
        
    @classmethod
    def create_empty(cls) -> HttpRequestBody:
        return HttpRequestBody(cls.BODY_EMPTY_STRING)
        
        
    def get_http_request_body_string(self) -> str:
        return self._http_request_body_string
    
    
    def get_http_request_body_bytes(self) -> bytes:
        return self._http_request_body_string.encode(self.ENCODING_BODY)
