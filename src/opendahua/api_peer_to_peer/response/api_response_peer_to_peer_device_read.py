from dataclasses import dataclass

from opendahua.api.api_response import ApiResponse
from opendahua.api_peer_to_peer.object.api_peer_to_peer_random_salt import ApiPeerToPeerRandomSalt
from opendahua.api_peer_to_peer.request.api_peer_to_peer_encryption_util import ApiPeerToPeerEncryptionUtil
from opendahua.api_peer_to_peer.response.api_response_peer_to_peer import ApiResponsePeerToPeer


@dataclass(frozen=True)
class ApiResponsePeerToPeerDeviceRead(ApiResponsePeerToPeer):
    _random_salt: ApiPeerToPeerRandomSalt
    
    # Field constants.
    FIELD_INFO = "Info"
    FIELD_RANDOM_SALT = "randsalt"

    @classmethod
    def parse(cls, value: dict) -> ApiResponse:
        device_info_encrypted = value[cls.FIELD_INFO]
        device_info_decrypted = ApiPeerToPeerEncryptionUtil.decrypt_device_info(device_info_encrypted)
        
        random_salt = ApiPeerToPeerRandomSalt(device_info_decrypted[cls.FIELD_RANDOM_SALT])
        
        return cls(random_salt)

    def get_random_salt(self) -> ApiPeerToPeerRandomSalt:
        return self._random_salt
