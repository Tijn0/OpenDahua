
class HttpResponseBody:
    # Body constants.
    BODY_EMPTY= b""
    
    # Encoding constants.
    ENCODING_BODY = "utf-8"
    
    # Number constants.
    NUMBER_OF_BYTE_BODY_PREVIEW = 64
    
    # Format constants.
    FORMAT_REPRESENTATION = "HttpResponseBody(size={size}, preview={preview})"
    
    def __init__(self, http_response_body_bytes: bytes):
        self._http_response_body_bytes: bytes = http_response_body_bytes
    
    
    @classmethod
    def create_empty(cls) -> HttpResponseBody:
        return HttpResponseBody(cls.BODY_EMPTY)
    
    
    def get_http_response_body_string(self) -> str:
        return self._http_response_body_bytes.decode(self.ENCODING_BODY)
    
    
    def get_http_response_body_bytes(self) -> bytes:
        return self._http_response_body_bytes
    
    
    def __repr__(self):
        preview = self._http_response_body_bytes[:self.NUMBER_OF_BYTE_BODY_PREVIEW]
        
        return self.FORMAT_REPRESENTATION.format(
            size=len(self._http_response_body_bytes),
            preview=repr(preview),
        )
