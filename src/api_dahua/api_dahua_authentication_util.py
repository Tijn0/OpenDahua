import hashlib
import re

from src.common_object.nonce import Nonce
from src.common_util.error_util import ErrorUtil
from src.dahua.dahua_device import DahuaDevice
from src.http.http_header import HttpHeader
from src.http.http_request import HttpRequest
from src.http.http_response import HttpResponse


class ApiDahuaAuthenticationUtil:
    # Header constants.
    HEADER_KEY_AUTHORIZATION = "Authorization"
    HEADER_KEY_DIGEST_AUTHENTICATION_REQUIRED = "WWW-Authenticate"

    # Format constants.
    FORMAT_HEADER_DIGEST = (
        "Digest "
        "username=\"{username}\", "
        "realm=\"{realm}\", "
        "nonce=\"{nonce}\", "
        "uri=\"{url_request}\", "
        "qop=\"{qop}\", "
        "nc={number_of_time_nonce_used:08x}, "
        "cnonce=\"{nonce_client}\", "
        "response=\"{response}\", "
        "opaque=\"{opaque}\""
    )
    FORMAT_HA1 = "{username}:{realm}:{password}"
    FORMAT_HA2 = "{http_request_method}:{url_request}"
    FORMAT_RESPONSE = "{ha1}:{nonce}:{number_of_time_nonce_used:08x}:{nonce_client}:{qop}:{ha2}"

    # Digest constants.
    DIGEST_QUALITY_OF_PROTECTION_AUTHENTICATION = "auth"
    DIGEST_NUMBER_OF_TIME_NONCE_USED = 1

    # Regex constants.
    REGEX_PATTERN_NONCE = re.compile(r'nonce="([^"]*)"')
    REGEX_PATTERN_REALM = re.compile(r'realm="([^"]*)"')

    @classmethod
    def determine_nonce_from_http_response_unauthorized(
            cls,
            http_response_unauthorized: HttpResponse,
    ) -> Nonce:
        header_digest_authentication_required = cls._get_header_digest_authentication_required(
            http_response_unauthorized,
        )
        
        match = cls.REGEX_PATTERN_NONCE.search(header_digest_authentication_required.get_header_value_string())
        
        return Nonce(match.group(1))
    
    @classmethod
    def determine_realm_from_http_response_unauthorized(
            cls,
            http_response_unauthorized: HttpResponse,
    ) -> str:
        header_digest_authentication_required = cls._get_header_digest_authentication_required(
            http_response_unauthorized,
        )
        
        match = cls.REGEX_PATTERN_REALM.search(header_digest_authentication_required.get_header_value_string())
        
        return match.group(1)
    
    @classmethod
    def _get_header_digest_authentication_required(cls, http_response_unauthorized: HttpResponse) -> HttpHeader:
        header_digest_authentication_required = http_response_unauthorized.get_header_or_none(
            cls.HEADER_KEY_DIGEST_AUTHENTICATION_REQUIRED,
        )
        
        if header_digest_authentication_required is None:
            raise ErrorUtil.create_error_unexpected_none_value(HttpHeader)
        else:
            return header_digest_authentication_required
    
    
    @classmethod
    def generate_header_authentication(
            cls,
            request: HttpRequest,
            device: DahuaDevice,
            nonce: Nonce,
            realm: str,
    ) -> HttpHeader:
        quality_of_protection = cls.DIGEST_QUALITY_OF_PROTECTION_AUTHENTICATION
        nonce_client = Nonce.create_random()
        
        ha1 = cls._hash_md5(
            cls.FORMAT_HA1.format(username=device.get_username(), realm=realm, password=device.get_password()),
        )
        ha2 = cls._hash_md5(
            cls.FORMAT_HA2.format(
                http_request_method=request.get_method().value,
                url_request=request.get_url().get_url_string(),
            ),
        )
        
        response = cls._hash_md5(
            cls.FORMAT_RESPONSE.format(
                ha1=ha1,
                nonce=nonce.get_nonce_string(),
                number_of_time_nonce_used=cls.DIGEST_NUMBER_OF_TIME_NONCE_USED,
                nonce_client=nonce_client.get_nonce_string(),
                qop=quality_of_protection,
                ha2=ha2,
            )
        )
        
        return HttpHeader(
            key=cls.HEADER_KEY_AUTHORIZATION,
            value=cls.FORMAT_HEADER_DIGEST.format(
                username=device.get_username(),
                realm=realm,
                nonce=nonce.get_nonce_string(),
                url_request=request.get_url().get_url_string(),
                qop=quality_of_protection,
                number_of_time_nonce_used=cls.DIGEST_NUMBER_OF_TIME_NONCE_USED,
                nonce_client=nonce_client.get_nonce_string(),
                response=response,
                opaque="",
            )
        )
    
    @staticmethod
    def _hash_md5(value: str) -> str:
        return hashlib.md5(value.encode()).hexdigest()
