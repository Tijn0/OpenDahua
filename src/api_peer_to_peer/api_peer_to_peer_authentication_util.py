import base64
import hashlib
from datetime import datetime, timezone

from src.common_object.nonce import Nonce
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
