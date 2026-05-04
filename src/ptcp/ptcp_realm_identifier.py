import random
from typing import Literal


class PtcpRealmIdentifier:
    # Random constants.
    MINIMUM_REALM_IDENTIFIER = 0x00000000
    MAXIMUM_REALM_IDENTIFIER = 0xFFFFFFFF
    
    # Byte constants.
    BYTE_LENGTH_REALM_IDENTIFIER = 4
    BYTE_ORDER_REALM_IDENTIFIER: Literal["big", "little"] = "big"
    
    # Realm identifier constants.
    REALM_IDENTIFIER_ZERO = 0

    def __init__(self, realm_identifier_int: int):
        self._realm_identifier_int: int = realm_identifier_int
    
    @classmethod
    def create_random(cls) -> PtcpRealmIdentifier:
        return PtcpRealmIdentifier(
            random.randint(cls.MINIMUM_REALM_IDENTIFIER, cls.MAXIMUM_REALM_IDENTIFIER),
        )
    
    @classmethod
    def ZERO(cls) -> PtcpRealmIdentifier:
        return cls(cls.REALM_IDENTIFIER_ZERO)
    
    def get_ptcp_realm_identifier_int(self) -> int:
        return self._realm_identifier_int
    
    def get_ptcp_realm_identifier_bytes(self) -> bytes:
        return self._realm_identifier_int.to_bytes(
            self.BYTE_LENGTH_REALM_IDENTIFIER,
            self.BYTE_ORDER_REALM_IDENTIFIER,
        )
    