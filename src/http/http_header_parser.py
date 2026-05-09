from src.http.http_header import HttpHeader


class HttpHeaderParser:
    # Separator constants.
    SEPARATOR_LINE_HEADER= b"\r\n"
    SEPARATOR_HEADER_KEY_VALUE= b": "
    
    # Encoding constants.
    ENCODING_HEADER = "ascii"


    @classmethod
    def parse_all(cls, header_bytes: bytes) -> list[HttpHeader]:
        all_header_parsed = []
        
        all_header_bytes = header_bytes.split(cls.SEPARATOR_LINE_HEADER)
        
        for header_bytes in all_header_bytes:
            all_header_parsed.append(cls.parse(header_bytes))
            
        return all_header_parsed
    
    
    @classmethod
    def parse(cls, header_bytes: bytes) -> HttpHeader:
        key_bytes, _, value_bytes = header_bytes.strip().partition(cls.SEPARATOR_HEADER_KEY_VALUE)
        
        return HttpHeader(key_bytes.decode(cls.ENCODING_HEADER), value_bytes.decode(cls.ENCODING_HEADER))
    