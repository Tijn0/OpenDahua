from src.api.api_request import T
from src.api_dahua.api_dahua_authentication_util import ApiDahuaAuthenticationUtil
from src.api_dahua.api_dahua_body_parser import ApiDahuaBodyParser
from src.api_dahua.request.api_request_dahua import ApiRequestDahua
from src.api_dahua.response.api_response_dahua_time_current_read import ApiResponseDahuaTimeCurrentRead
from src.common_object.dahua_error import DahuaError
from src.common_object.nonce import Nonce
from src.common_util.error_util import ErrorUtil
from src.dahua.dahua_device import DahuaDevice
from src.http.http_request import HttpRequest
from src.http.http_response import HttpResponse
from src.http.http_status_code import HttpStatusCode
from src.ptcp.ptcp_http_client import PtcpHttpClient
from src.signaling_client import SignalingClient

class ApiClientDahua:
    # Error constants.
    ERROR_DAHUA_API = "Received error response Dahua API: \"{http_response}\"."
    

    def __init__(self, device: DahuaDevice):
        self._device: DahuaDevice = device
        self._signaling_client: SignalingClient = SignalingClient(device)
        
        self._http_client: PtcpHttpClient|None = None
        self._nonce: Nonce|None = None
        self._realm: str|None = None
        self._number_of_time_nonce_used = 1

        
    async def send_request(self, api_request: ApiRequestDahua[T]) -> T:
        client = await self._get_http_client()
        
        http_request = api_request.generate_http_request()
        http_request = self._add_header_authentication_if_needed(http_request)
        
        http_response = await client.send_request(http_request)
        
        if self._is_http_response_success(http_response):
            self._number_of_time_nonce_used += 1
            
            return self._parse_api_response(api_request, http_response)
        elif http_response.get_status_code() == HttpStatusCode.UNAUTHORIZED:
            self._initialize_digest_authentication(http_response)
            
            return await self.send_request(api_request)
        else:
            self._number_of_time_nonce_used += 1
            
            raise DahuaError(self.ERROR_DAHUA_API.format(http_response=http_response))
        
        
    def _add_header_authentication_if_needed(self, http_request: HttpRequest) -> HttpRequest:
        if self._nonce is None or self._realm is None:
            # We don't have a nonce yet.
            pass
        else:
            header_authentication = ApiDahuaAuthenticationUtil.generate_header_authentication(
                http_request,
                self._device,
                self._nonce,
                self._realm,
                self._number_of_time_nonce_used,
            )
            http_request.add_header(header_authentication)
        
        return http_request

        
    async def _get_http_client(self) -> PtcpHttpClient:
        if self._http_client is None:
            ptcp_socket = await self._signaling_client.connect()
            await ptcp_socket.start()
            http_client = PtcpHttpClient(ptcp_socket)
            self._http_client = http_client
            
            return http_client
        else:
            return self._http_client
        
        
    def _is_http_response_success(self, http_response: HttpResponse) -> bool:
        return http_response.get_status_code() in self._get_all_http_status_code_success()
    
        
    @staticmethod
    def _get_all_http_status_code_success() -> list[HttpStatusCode]:
        return [
            HttpStatusCode.OK,
        ]
    
    def _parse_api_response(self, api_request: ApiRequestDahua[T], http_response: HttpResponse) -> T:
        response_class = api_request.get_response_class()
        response_body = http_response.get_body()
        response_body_dict = ApiDahuaBodyParser.determine_dict(response_body.get_http_response_body_string())

        match response_class:
            case _ if response_class is ApiResponseDahuaTimeCurrentRead:
                return ApiResponseDahuaTimeCurrentRead.parse(response_body_dict)
            case _:
                raise ErrorUtil.create_error_unexpected_class(response_class)
            
            
    def _initialize_digest_authentication(self, http_response_unauthorized: HttpResponse) -> None:
        self._nonce = ApiDahuaAuthenticationUtil.determine_nonce_from_http_response_unauthorized(
            http_response_unauthorized,
        )
        self._realm = ApiDahuaAuthenticationUtil.determine_realm_from_http_response_unauthorized(
            http_response_unauthorized,
        )
        self._number_of_time_nonce_used = 1
        