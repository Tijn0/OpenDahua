import random


class Cookie:
    # Length constants.
    LENGTH_COOKIE = 4
    
    def __init__(self, cookie_bytes: bytes) -> None:
        self._cookie_bytes: bytes = cookie_bytes
        
    @staticmethod
    def create_random() -> Cookie:
        return Cookie(random.randbytes(Cookie.LENGTH_COOKIE))
    
    def get_cookie_bytes(self) -> bytes:
        return self._cookie_bytes
