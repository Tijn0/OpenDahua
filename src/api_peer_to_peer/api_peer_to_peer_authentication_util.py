import base64
import hashlib
import hmac
import time
from datetime import datetime, timezone

from src.api_peer_to_peer.object.api_peer_to_peer_random_salt import ApiPeerToPeerRandomSalt
from src.common_object.key import Key
from src.common_object.nonce import Nonce
from src.dahua.dahua_device import DahuaDevice
from src.http.http_header import HttpHeader


class ApiPeerToPeerAuthenticationUtil:
    # Authentication constants.
    AUTHENTICATION_USERNAME = "cba1b29e32cb17aa46b8ff9e73c7f40b"
    AUTHENTICATION_KEY = "996103384cdf19179e19243e959bbf8b"

    # Header constants.
    HEADER_AUTHORIZATION_KEY = "Authorization"
    HEADER_AUTHORIZATION_VALUE = "WSSE profile=\"UsernameToken\""
    HEADER_WEB_SERVICES_SECURITY_KEY = "X-WSSE"
    HEADER_WEB_SERVICES_SECURITY_VALUE = (
        "UsernameToken "
        "Username=\"{username}\", "
        "PasswordDigest=\"{digest}\", "
        "Nonce=\"{nonce}\", "
        "Created=\"{time_created}\", "
    )
    
    # Format constants.
    FORMAT_TIME_CREATED = "%Y-%m-%dT%H:%M:%SZ"
    FORMAT_PASSWORD = "{nonce}{time_created}DHP2P:{username}:{authentication_key}"
    FORMAT_MESSAGE_AUTHENTICATION = "{nonce}{time_epoch_now}{payload}"
    FORMAT_PART_BODY_AUTHENTICATION = (
        "<CreateDate>{time_epoch_now}</CreateDate>"
        "<DevAuth>{authentication_token}</DevAuth>"
        "<Nonce>{nonce}</Nonce>"
        "<RandSalt>{random_salt}</RandSalt>"
        "<UserName>{username}</UserName>"
    )
    FORMAT_AUTHENTICATION_KEY_PAYLOAD = "{username}:Login to {random_salt}:{password}"

    @classmethod
    def generate_header_authorization(cls) -> HttpHeader:
        return HttpHeader(cls.HEADER_AUTHORIZATION_KEY, cls.HEADER_AUTHORIZATION_VALUE)
    
    
    @classmethod
    def generate_header_authentication(cls) -> HttpHeader:
        nonce = Nonce.create_random()
        time_created = datetime.now(timezone.utc)
        digest = cls._determine_digest(nonce, time_created)
        
        return HttpHeader(
            cls.HEADER_WEB_SERVICES_SECURITY_KEY,
            cls.HEADER_WEB_SERVICES_SECURITY_VALUE.format(
                username=cls.AUTHENTICATION_USERNAME,
                digest=digest,
                nonce=nonce.get_nonce_string(),
                time_created=time_created.strftime(cls.FORMAT_TIME_CREATED),
            ),
        )
    
    
    @classmethod
    def _determine_digest(cls, nonce: Nonce, time_created: datetime) -> str:
        password = cls.FORMAT_PASSWORD.format(
            nonce=nonce.get_nonce_string(),
            time_created=time_created.strftime(cls.FORMAT_TIME_CREATED),
            username=cls.AUTHENTICATION_USERNAME,
            authentication_key=cls.AUTHENTICATION_KEY,
        )
        
        # TODO: kan dit in een?
        hash_digest = hashlib.sha1()
        hash_digest.update(password.encode())
        
        digest = base64.b64encode(hash_digest.digest()).decode()
        
        return digest
    
    
    @classmethod
    def generate_part_body_authentication(
            cls,
            device: DahuaDevice,
            key_authentication: Key,
            payload: str,
            nonce: Nonce,
            random_salt: ApiPeerToPeerRandomSalt,
    ) -> str:
        time_epoch_now = int(time.time())
        
        message_authentication = cls.FORMAT_MESSAGE_AUTHENTICATION.format(
            nonce=nonce.get_nonce_string(),
            time_epoch_now=time_epoch_now,
            payload=payload,
        ).encode()
        authentication_token = base64.b64encode(hmac.new(key_authentication.get_key_bytes(), message_authentication, hashlib.sha256).digest()).decode()
        
        return cls.FORMAT_PART_BODY_AUTHENTICATION.format(
            time_epoch_now=time_epoch_now,
            authentication_token=authentication_token,
            nonce=nonce.get_nonce_string(),
            random_salt=random_salt.get_random_salt_string(),
            username=device.get_username(),
        )


    # TODO: custom type.
    @classmethod
    def generate_key_authentication(cls, device: DahuaDevice, random_salt: ApiPeerToPeerRandomSalt) -> Key:
        # TODO: Dit uit de device read response halen.
        payload = cls.FORMAT_AUTHENTICATION_KEY_PAYLOAD.format(
            username=device.get_username(),
            random_salt=random_salt.get_random_salt_string(),
            password=device.get_password(),
        )
        
        key_bytes = hashlib.md5(payload.encode()).hexdigest().upper().encode()
        
        return Key(key_bytes)
