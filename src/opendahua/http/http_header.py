

class HttpHeader:
    # Format constants.
    FORMAT_HTTP_HEADER_STRING = "{key}: {value}"
    
    
    def __init__(self, key: str, value: str) -> None:
        self._key: str = key
        self._value: str = value
        
        
    def get_header_key_string(self) -> str:
        return self._key
    
    
    def get_header_value_string(self) -> str:
        return self._value
    
    
    def get_http_header_string(self) -> str:
        return self.FORMAT_HTTP_HEADER_STRING.format(key=self._key, value=self._value)
    
    
    def __str__(self):
        return self.get_http_header_string()


    def __repr__(self):
        return self.get_http_header_string()
