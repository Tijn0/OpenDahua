

class PtcpPacketIdentifier:
    # Ptcp constants.
    PTCP_PACKET_IDENTIFIER_INT_MAXIMUM = 0x0000FFFF
    PTCP_PACKET_IDENTIFIER_INT_ZERO = 0
    PTCP_PACKET_IDENTIFIER_INT_SYN = 0x0002FFFF

    # Count constants.
    COUNT_INCREMENT = 1
    COUNT_DECREMENT = 1

    def __init__(self, ptcp_packet_identifier_int: int) -> None:
        self._ptcp_packet_identifier_int: int = ptcp_packet_identifier_int
        
    @classmethod
    def create_maximum(cls) -> PtcpPacketIdentifier:
        return cls(cls.PTCP_PACKET_IDENTIFIER_INT_MAXIMUM)
    
    @classmethod
    def ZERO(cls) -> PtcpPacketIdentifier:
        return cls(cls.PTCP_PACKET_IDENTIFIER_INT_ZERO)
    
    @classmethod
    def SYN(cls) -> PtcpPacketIdentifier:
        return cls(cls.PTCP_PACKET_IDENTIFIER_INT_SYN)
    
    def subtract(self, amount: int) -> PtcpPacketIdentifier:
        return PtcpPacketIdentifier(self._ptcp_packet_identifier_int - amount)
    
    def increment(self) -> PtcpPacketIdentifier:
        return PtcpPacketIdentifier(self._ptcp_packet_identifier_int + self.COUNT_INCREMENT)
    
    def decrement(self) -> PtcpPacketIdentifier:
        return PtcpPacketIdentifier(self._ptcp_packet_identifier_int - self.COUNT_DECREMENT)
    
    def get_ptcp_packet_identifier_int(self) -> int:
        return self._ptcp_packet_identifier_int
