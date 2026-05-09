from src.http.http_header_parser import HttpHeaderParser
from src.http.http_response import HttpResponse
from src.http.http_response_body import HttpResponseBody
from src.http.http_status_code import HttpStatusCode


# TODO: zorgen dat alles niet opnieuw geparsed hoeft te worden bij nieuwe chunks.
class HttpResponseParser:
    # Error constants.
    ERROR_BODY_SIZE_EXCEEDING_CONTENT_LENGTH = "The body is size is exceeding the content length header."
    
    # Buffer constants.
    BUFFER_EMPTY = b""
    
    # Separator constants.
    SEPARATOR_HEADER_BODY = b"\r\n\r\n"
    SEPARATOR_STATUS_LINE_HEADER = b"\r\n"
    SEPARATOR_STATUS_ITEM = b" "

    # Header constants.
    HEADER_KEY_CONTENT_LENGTH = "content-length"
    
    # Encoding constants.
    ENCODING_STATUS_LINE = "ascii"
    
    
    @classmethod
    def parse(cls, data: bytes) -> HttpResponse:
        response_info_bytes, _, body_bytes = data.partition(cls.SEPARATOR_HEADER_BODY)
        status_line_bytes, _, header_bytes = data.partition(cls.SEPARATOR_STATUS_LINE_HEADER)
        
        all_header = HttpHeaderParser.parse_all(header_bytes)
        _, status_code_bytes, _ = status_line_bytes.split(cls.SEPARATOR_STATUS_ITEM)
        status_code = HttpStatusCode(int(status_code_bytes.decode(cls.ENCODING_STATUS_LINE)))
        
        if body_bytes == HttpResponseBody.create_empty().get_http_response_body_bytes():
            # Response doesn't have a body.
            body = None
            pass
        else:
            body = HttpResponseBody.create_from_bytes(body_bytes)
        
        return HttpResponse(status_code, all_header, body)
        
        
    @classmethod
    def is_complete(cls, buffer: bytes) -> bool:
        return (cls._is_part_header_complete(buffer) and
            cls._is_part_body_complete(buffer))
            
    
    @classmethod
    def _is_part_header_complete(cls, buffer: bytes) -> bool:
        if cls.SEPARATOR_HEADER_BODY in buffer:
            return True
        else:
            return False
        

    @classmethod
    def _is_part_body_complete(cls, buffer: bytes) -> bool:
        response_info_bytes, _, body_bytes = buffer.partition(cls.SEPARATOR_HEADER_BODY)
        status_line, _, header_bytes = response_info_bytes.partition(cls.SEPARATOR_STATUS_LINE_HEADER)
        
        content_length = cls._parse_content_length_or_none(header_bytes)
        
        if content_length is None:
            # If the header part doesn't have a content length header then the body is complete.
            return True
        else:
            length_body = len(body_bytes)
            
            if length_body == content_length:
                return True
            elif length_body <= content_length:
                return False
            else:
                raise Exception(cls.ERROR_BODY_SIZE_EXCEEDING_CONTENT_LENGTH)
        
        
    @classmethod
    def _parse_content_length_or_none(cls, header_bytes: bytes) -> int|None:
        all_header = HttpHeaderParser.parse_all(header_bytes)
        
        for header in all_header:
            if header.get_header_key_string().lower() == cls.HEADER_KEY_CONTENT_LENGTH:
                return int(header.get_header_value_string())
            else:
                # Header is not content length header, keep looking.
                pass
        
        return None
    