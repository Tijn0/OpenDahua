import random


class PtcpRealmIdentifier:
    # Random constants.
    MINIMUM_REALM_IDENTIFIER = 0x00000000
    MAXIMUM_REALM_IDENTIFIER = 0xFFFFFFFF
    
    def __init__(self, realm_identifier_int: int) -> None:
        self._realm_identifier_int: int = realm_identifier_int
    
    @classmethod
    def create_random(cls) -> PtcpRealmIdentifier:
        return PtcpRealmIdentifier(
            random.randint(cls.MINIMUM_REALM_IDENTIFIER, cls.MAXIMUM_REALM_IDENTIFIER),
        )
    
    def get_ptcp_realm_identifier_int(self) -> int:
        return self._realm_identifier_int
