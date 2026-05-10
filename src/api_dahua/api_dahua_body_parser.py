from src.common_object.dahua_error import DahuaError
from src.common_util.error_util import ErrorUtil
from src.http.http_header import HttpHeader
from src.http.http_response import HttpResponse


class ApiDahuaBodyParser:
    # Error constants.
    ERROR_UNEXPECTED_CONTENT_TYPE = "Unexpected content type \"{content_type}\"."
    
    # Separator constants.
    SEPARATOR_LINE_BODY = "\r\n"
    SEPARATOR_KEY_VALUE = "="
    
    # TODO: verplaats http logica naar http response zelf
    # Header constants.
    HEADER_CONTENT_TYPE = "Content-type"
    
    # Content constants.
    CONTENT_TYPE_TEXT_PLAIN = "text/plain"
    CONTENT_TYPE_TEXT_PLAIN_CHARSET_UTF_8 = "text/plain;charset=utf-8"
    CONTENT_TYPE_APPLICATION_HTTP = "application/http"
    
    # Field constants.
    FIELD_DATA = "data"
    

    @classmethod
    def determine_dict(cls, http_response: HttpResponse) -> dict:
        content_type_response = cls.determine_content_type_response(http_response)
        
        # TODO: Iets van should_use_key_value_parsing.
        if content_type_response == cls.CONTENT_TYPE_TEXT_PLAIN or content_type_response == cls.CONTENT_TYPE_TEXT_PLAIN_CHARSET_UTF_8:
            return cls._parse_key_value(http_response.get_body().get_http_response_body_string())
        elif content_type_response == cls.CONTENT_TYPE_APPLICATION_HTTP:
            return {cls.FIELD_DATA: http_response.get_body().get_http_response_body_bytes()}
        else:
            raise DahuaError(cls.ERROR_UNEXPECTED_CONTENT_TYPE.format(content_type=content_type_response))
        
        
    @classmethod
    def determine_content_type_response(cls, http_response: HttpResponse) -> str:
        header_content_type = http_response.get_header_or_none(cls.HEADER_CONTENT_TYPE)
        
        if header_content_type is None:
            raise ErrorUtil.create_error_unexpected_none_value(HttpHeader)
        else:
            return header_content_type.get_header_value_string()
    
    
    @classmethod
    def _parse_key_value(cls, body_string: str) -> dict:
        response_dict = {}
        body_string_excluding_trailing_carriage_return = body_string.strip()
        
        all_line_body = body_string_excluding_trailing_carriage_return.split(cls.SEPARATOR_LINE_BODY)
        
        for line_body in all_line_body:
            if cls.SEPARATOR_KEY_VALUE in line_body:
                key, value = line_body.split(cls.SEPARATOR_KEY_VALUE)
                
                response_dict[key] = value
            else:
                # Line is not a key value pair. Ignore it.
                pass
        
        return response_dict
    