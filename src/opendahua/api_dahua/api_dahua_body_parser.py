import re
from datetime import datetime
from typing import Any

from opendahua.common_object.dahua_error import DahuaError
from opendahua.common_util.error_util import ErrorUtil
from opendahua.http.http_header import HttpHeader
from opendahua.http.http_response import HttpResponse


class ApiDahuaBodyParser:
    # Error constants.
    ERROR_UNEXPECTED_CONTENT_TYPE = "Unexpected content type \"{content_type}\"."
    
    # Separator constants.
    SEPARATOR_LINE_BODY = "\r\n"
    SEPARATOR_KEY_VALUE = "="
    SEPARATOR_PART_KEY = "."

    # TODO: verplaats http logica naar http response zelf
    # Header constants.
    HEADER_CONTENT_TYPE = "Content-type"
    
    # Content constants.
    CONTENT_TYPE_TEXT_PLAIN = "text/plain"
    CONTENT_TYPE_TEXT_PLAIN_CHARSET_UTF_8 = "text/plain;charset=utf-8"
    CONTENT_TYPE_APPLICATION_HTTP = "application/http"
    
    # Field constants.
    FIELD_DATA = "data"
    
    # Regex constants.
    REGEX_PART_KEY_LIST = r"^(?P<key>[a-zA-Z]+)\[(?P<index>\d+)\]$"
    REGEX_MATCH_GROUP_KEY = "key"
    REGEX_MATCH_GROUP_INDEX = "index"
    
    # Index constants.
    INDEX_FIRST = 0


    @classmethod
    def determine_dict(cls, http_response: HttpResponse) -> dict:
        content_type_response = cls.determine_content_type_response(http_response)
        
        # TODO: Iets van should_use_key_value_parsing.
        if content_type_response == cls.CONTENT_TYPE_TEXT_PLAIN or content_type_response == cls.CONTENT_TYPE_TEXT_PLAIN_CHARSET_UTF_8:
            return cls.parse_body_key_value(http_response.get_body().get_http_response_body_string())
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
    def parse_body_key_value(cls, body_string: str) -> dict:
        response_dict = {}
        body_string_excluding_trailing_carriage_return = body_string.strip()
        
        all_line_body = body_string_excluding_trailing_carriage_return.split(cls.SEPARATOR_LINE_BODY)
        
        for line_body in all_line_body:
            cls._parse_key_value(line_body, response_dict)
        
        return response_dict
    
    @classmethod
    def _parse_key_value(cls, key_value_string: str, response_dict: dict) -> dict:
        key_string_full, _, _ = key_value_string.partition(cls.SEPARATOR_KEY_VALUE)
        is_key_nested = cls.SEPARATOR_PART_KEY in key_string_full
        
        separator = cls.SEPARATOR_PART_KEY if is_key_nested else cls.SEPARATOR_KEY_VALUE
        key, _, remainder_string = key_value_string.partition(separator)
        
        match_list = re.search(cls.REGEX_PART_KEY_LIST, key)
        
        if match_list:
            key_list = match_list.group(cls.REGEX_MATCH_GROUP_KEY)
            index_list_item = int(match_list.group(cls.REGEX_MATCH_GROUP_INDEX))
            
            all_list_item = response_dict.setdefault(key_list, [])
            is_list_item_existing = index_list_item < len(all_list_item)
            
            if is_key_nested:
                if is_list_item_existing:
                    list_item_dict = all_list_item[index_list_item]
                else:
                    list_item_dict = {}
                    
                list_item_dict_updated = cls._parse_key_value(remainder_string, list_item_dict)
            else:
                value_string = remainder_string
                
                list_item_dict_updated = cls._parse_value(value_string)
            
            if is_list_item_existing:
                all_list_item[index_list_item] = list_item_dict_updated
            else:
                all_list_item.append(list_item_dict_updated)
        
        else:
            if is_key_nested:
                value_current = response_dict.get(key, {})
                value_updated = cls._parse_key_value(remainder_string, value_current)
            else:
                value_string = remainder_string
                
                value_updated = cls._parse_value(value_string)
            
            response_dict[key] = value_updated
        
        return response_dict
    

    @classmethod
    def _parse_value(cls, value_string: str) -> Any:
        if value_string.isdigit():
            return int(value_string)
        elif cls._is_datetime_string(value_string):
            return cls._parse_datetime_string(value_string)
        else:
            return value_string
        
    
    @classmethod
    def _is_datetime_string(cls, value_string: str) -> bool:
        try:
            cls._parse_datetime_string(value_string)
            
            return True
        except ValueError:
            return False
    
    
    @classmethod
    def _parse_datetime_string(cls, value_string: str) -> datetime:
        try:
            return datetime.fromisoformat(value_string)
        except ValueError:
            # TODO: magic number.
            return datetime.strptime(value_string, "%Y-%m-%d %H:%M:%S")
