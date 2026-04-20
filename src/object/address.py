import socket


class Address:
    # Format constants.
    FORMAT_ADDRESS = "{ip}:{port}"
    
    # Separator constants.
    SEPARATOR_IP_PORT = ":"
    
    # Index constants.
    INDEX_IP = 0
    INDEX_PORT = 1

    # Encoding constants.
    ENCODING_LENGTH_NUMBER_OF_BYTE_PORT = 2

    def __init__(self, address_string: str):
        self._address_string: str = address_string
        
    @staticmethod
    def create_from_ip_and_port(ip: str, port: int) -> Address:
        return Address(Address.FORMAT_ADDRESS.format(ip=ip, port=port))
        
    def get_ip(self) -> str:
        return self._address_string.split(self.SEPARATOR_IP_PORT)[self.INDEX_IP]
    
    def get_port(self) -> int:
        return int(self._address_string.split(self.SEPARATOR_IP_PORT)[self.INDEX_PORT])

    def get_address_string(self) -> str:
        return self._address_string
    
    def get_address_encoded(self) -> bytes:
        """Encodes the address in the Dahua specific format used in PTCP."""
        port_encoded = self.get_port().to_bytes(self.ENCODING_LENGTH_NUMBER_OF_BYTE_PORT)
        ip_encoded = socket.inet_aton(self.get_ip())
        
        address_encoded = port_encoded + ip_encoded
        
        return bytes(0xFF - byte for byte in address_encoded)