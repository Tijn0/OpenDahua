import random
from typing import Literal


class RealmIdentifier:
    # Random constants.
    MINIMUM_REALM_IDENTIFIER = 0x00000000
    MAXIMUM_REALM_IDENTIFIER = 0xFFFFFFFF
    
    # Byte constants.
    BYTE_LENGTH_REALM_IDENTIFIER = 4
    BYTE_ORDER_REALM_IDENTIFIER: Literal["big", "little"] = "big"

    def __init__(self, realm_identifier_int: int):
        self._realm_identifier_int: int = realm_identifier_int
    
    @staticmethod
    def create_random() -> RealmIdentifier:
        return RealmIdentifier(
            random.randint(RealmIdentifier.MINIMUM_REALM_IDENTIFIER, RealmIdentifier.MAXIMUM_REALM_IDENTIFIER),
        )
    
    def get_realm_identifier_int(self) -> int:
        return self._realm_identifier_int
    
    def get_realm_identifier_bytes(self) -> bytes:
        return self._realm_identifier_int.to_bytes(
            self.BYTE_LENGTH_REALM_IDENTIFIER,
            self.BYTE_ORDER_REALM_IDENTIFIER,
        )
    