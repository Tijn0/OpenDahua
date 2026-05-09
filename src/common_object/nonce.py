from secrets import token_hex

class Nonce:
    # Number constants.
    NUMBER_OF_BYTES_NONCE = 8
    
    def __init__(self, nonce_string: str):
        self._nonce_string: str = nonce_string
        
    def get_nonce_string(self) -> str:
        return self._nonce_string

    @classmethod
    def create_random(cls) -> Nonce:
        return cls(token_hex(cls.NUMBER_OF_BYTES_NONCE))
    