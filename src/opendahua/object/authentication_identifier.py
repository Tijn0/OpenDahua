import random


class AuthenticationIdentifier:
    # Length constants.
    LENGTH_AUTHENTICATION_IDENTIFIER = 8
    
    # Character constants.
    CHARACTER_SPACE = " "
    
    def __init__(self, authentication_identifier_bytes: bytes):
        self._authentication_identifier_bytes: bytes = authentication_identifier_bytes
    
    @staticmethod
    def create_random() -> AuthenticationIdentifier:
        return AuthenticationIdentifier(random.randbytes(AuthenticationIdentifier.LENGTH_AUTHENTICATION_IDENTIFIER))
        
    def get_authentication_identifier_bytes(self) -> bytes:
        return self._authentication_identifier_bytes
    
    def get_authentication_identifier_string(self) -> str:
        # TODO: magic nummer weghalen
        return self.CHARACTER_SPACE.join(f'{byte:x}' for byte in self._authentication_identifier_bytes)
        
    def get_authentication_identifier_bytes_inverted(self) -> bytes:
        return bytes(0xFF - byte for byte in self._authentication_identifier_bytes)