from opendahua.common_object.dahua_error import DahuaError
from opendahua.http.http_header_parser import HttpHeaderParser
from opendahua.http.http_response import HttpResponse
from opendahua.http.http_response_body import HttpResponseBody
from opendahua.http.http_status_code import HttpStatusCode


class HttpResponseParser:
    # Error constants.
    ERROR_BODY_SIZE_EXCEEDING_CONTENT_LENGTH = "The body is size is exceeding the content length header."
    ERROR_HEADER_INCOMPLETE = "The headers are still incomplete."
    ERROR_CONTENT_HEADER_MISSING = "The response doesn't contain a content-length header."
    ERROR_RESPONSE_INCOMPLETE = "The response is still incomplete."

    # Separator constants.
    SEPARATOR_HEADER_BODY = b"\r\n\r\n"
    SEPARATOR_STATUS_LINE_HEADER = b"\r\n"
    SEPARATOR_STATUS_ITEM = b" "

    # Header constants.
    HEADER_KEY_CONTENT_LENGTH = "content-length"
    
    # Encoding constants.
    ENCODING_STATUS_LINE = "ascii"
    
    # Index constants.
    INDEX_NOT_FOUND = -1
    
    def __init__(self) -> None:
        self._buffer: bytearray = bytearray()
        self._index_header_end: int|None = None
        self._content_length: int|None = None
        
        
    def feed(self, chunk: bytes) -> None:
        self._buffer += chunk
        
        if self._index_header_end is None:
            index_separator_header_body = self._buffer.find(self.SEPARATOR_HEADER_BODY)
            
            if index_separator_header_body == self.INDEX_NOT_FOUND:
                # Headers haven't ended yet.
                pass
            else:
                self._index_header_end = index_separator_header_body + len(self.SEPARATOR_HEADER_BODY)
                self._content_length = self._parse_content_length_or_none_from_buffer()
        else:
            # Headers already complete.
            pass
        
            
    def build(self) -> HttpResponse:
        self._assert_response_is_complete()
        
        response_info_bytes, _, body_bytes = self._buffer.partition(self.SEPARATOR_HEADER_BODY)
        status_line_bytes, _, header_bytes = response_info_bytes.partition(self.SEPARATOR_STATUS_LINE_HEADER)
        
        all_header = HttpHeaderParser.parse_all(header_bytes)
        # TODO: magic number
        _, status_code_bytes, _ = status_line_bytes.split(self.SEPARATOR_STATUS_ITEM, 2)
        status_code = HttpStatusCode(int(status_code_bytes.decode(self.ENCODING_STATUS_LINE)))
        
        body = HttpResponseBody(body_bytes)
        
        return HttpResponse(status_code, all_header, body)
        
        
    def is_complete(self) -> bool:
        if self._index_header_end is None:
            return False
        elif self._content_length is None:
            # Headers are complete and the content-length header is not present.
            # We can assume the response doesn't have a body, so the request is complete.
            return True
        elif self._is_body_complete(self._content_length):
            return True
        else:
            return False
        
        
    def _is_body_complete(self, content_length: int) -> int:
        number_of_bytes_body = len(self._buffer) - self._index_header_end
        
        if number_of_bytes_body < content_length:
            # Body is incomplete.
            return False
        elif number_of_bytes_body == content_length:
            return True
        else:
            raise DahuaError(self.ERROR_BODY_SIZE_EXCEEDING_CONTENT_LENGTH)
        
    
    def _parse_content_length_or_none_from_buffer(self) -> int|None:
        header_bytes = self._get_header_bytes()
        all_header = HttpHeaderParser.parse_all(header_bytes)
        
        for header in all_header:
            if header.get_header_key_string().lower() == self.HEADER_KEY_CONTENT_LENGTH:
                return int(header.get_header_value_string())
            else:
                # Header is not content length header, keep looking.
                pass
        
        return None
    
    
    def _get_header_bytes(self) -> bytes:
        index_header_end = self._index_header_end
        
        if index_header_end is None:
            raise DahuaError(self.ERROR_HEADER_INCOMPLETE)
        else:
            return bytes(self._buffer[: index_header_end - len(self.SEPARATOR_HEADER_BODY)])
    
    
    def _assert_response_is_complete(self) -> None:
        if self.is_complete():
            # All good.
            pass
        else:
            raise DahuaError(self.ERROR_RESPONSE_INCOMPLETE)
