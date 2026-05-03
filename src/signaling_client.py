from src.object.dahua_device import DahuaDevice


class SignalingClient:
    # Error constants.
    ERROR_NO_RESPONSE_FROM_DEVICE = "Timeout occurred while waiting for a response from the device. Is the firewall letting it through?"
    
    # Endpoint constants.
    ENDPOINT_PEER_TO_PEER_SERVER_PROBE = "/probe/p2psrv"
    ENDPOINT_PEER_TO_PEER_SERVER_INFO = "/online/p2psrv/{serial_number}"
    ENDPOINT_DEVICE_PROBE = "/probe/device/{serial_number}"
    ENDPOINT_DEVICE_INFO = "/info/device/{serial_number}"
    ENDPOINT_DEVICE_PEER_TO_PEER_CHANNEL = "/device/{serial_number}/p2p-channel"
    
    # Field constants.
    FIELD_DATA = "data"
    FIELD_BODY = "body"
    FIELD_ADDRESS_SERVER_PEER_TO_PEER = "US"
    FIELD_ADDRESS_DEVICE_LOCAL_ENCRYPTED = "LocalAddr"
    FIELD_ADDRESS_DEVICE_PUBLIC = "PubAddr"
    FIELD_NONCE = "Nonce"
    
    # IP constants.
    IP_LOOPBACK = "127.0.0.1"
    
    # Part constants.
    PART_BODY_ADDRESS_LOCAL_ENCRYPTED = "<IpEncrptV2>true</IpEncrptV2><LocalAddr>{address_local_encrypted}</LocalAddr>"
    
    # Body constants.
    BODY_DEVICE_PEER_TO_PEER_CHANNEL = "<body>{header_authentication}<Identify>{authentication_identifier}</Identify>{part_body_address_local_encrypted}<version>5.0.0</version></body>"
    
    # Separator constants.
    SEPARATOR_ADDRESS = ":"
    
    # Index constants.
    INDEX_ALL_ADDRESS_DEVICE = 1
    INDEX_ADDRESS_DEVICE = 1
    INDEX_PORT_DEVICE = 1
    INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_START = 8
    INDEX_PTCP_RESPONSE_TRANSACTION_IDENTIFIER_END = 20
    
    # Number constants.
    NUMBER_OF_PACKET_HOLE_PUNCH = 4
    
    def __init__(self, device: DahuaDevice):
        self._device = device
        
    def connect(self) ->:
    