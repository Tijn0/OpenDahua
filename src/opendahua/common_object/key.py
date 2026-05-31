

class Key:
    def __init__(self, key_bytes: bytes) -> None:
        self._key_bytes: bytes = key_bytes
        
    def get_key_bytes(self) -> bytes:
        return self._key_bytes
