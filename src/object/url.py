from urllib.parse import urlparse


class Url:
    # Path constants.
    PATH_ROOT = "/"
    
    def __init__(self, url_string: str):
        self._assert_is_valid(url_string)
        
        self._url_string: str = url_string
    
    
    def _assert_is_valid(self, url_string: str) -> None:
        if self.is_valid(url_string):
            # All good.
            pass
        else:
            raise ValueError
    
    
    @staticmethod
    def is_valid(url_string: str) -> bool:
        url_parsed = urlparse(url_string)
        
        return bool(url_parsed.netloc or url_parsed.path)


    def get_url_string(self) -> str:
        return self._url_string


    def get_path_string(self) -> str:
        path = urlparse(self._url_string).path
        
        if path:
            return path
        else:
            return self.PATH_ROOT


    def get_host_string_or_none(self) -> str|None:
        host = urlparse(self._url_string).netloc
        
        if host:
            return host
        else:
            return None
