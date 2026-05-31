from opendahua.api.api_request import T
from opendahua.api_dahua.api_dahua_authentication_util import ApiDahuaAuthenticationUtil
from opendahua.api_dahua.api_dahua_body_parser import ApiDahuaBodyParser
from opendahua.api_dahua.request.api_request_dahua import ApiRequestDahua
from opendahua.common_object.dahua_error import DahuaError
from opendahua.common_object.dahua_error_bad_request import DahuaErrorBadRequest
from opendahua.common_object.nonce import Nonce
from opendahua.dahua.dahua_device import DahuaDevice
from opendahua.http.http_request import HttpRequest
from opendahua.http.http_response import HttpResponse
from opendahua.http.http_status_code import HttpStatusCode
from opendahua.ptcp.ptcp_http_client import PtcpHttpClient
from opendahua.signaling_client import SignalingClient

class ApiClientDahua:
    # Error constants.
    ERROR_DAHUA_API = "Received error response from Dahua API: \"{http_response}\"."
    ERROR_ALREADY_CONNECTED = "Already connected."
    ERROR_ALREADY_DISCONNECTED = "Already disconnected."
    ERROR_EXPECTED_DIGEST_CHALLENGE = "Received response with status code \"{status_code}\" instead of digest authentication challenge."
    ERROR_NOT_CONNECTED = "You have to use connect() to connect to the device before making API requests."


    def __init__(self, device: DahuaDevice):
        self._device: DahuaDevice = device
        self._signaling_client: SignalingClient = SignalingClient(device)
        self._http_client: PtcpHttpClient|None = None


    async def connect(self) -> None:
        if self._http_client is None:
            ptcp_socket = await self._signaling_client.connect()
            
            http_client = PtcpHttpClient(ptcp_socket)
            
            await http_client.connect()
            self._http_client = http_client
        else:
            raise DahuaError(self.ERROR_ALREADY_CONNECTED)
    
    
    async def disconnect(self) -> None:
        if self._http_client is None:
            raise DahuaError(self.ERROR_ALREADY_DISCONNECTED)
        else:
            await self._http_client.disconnect()
        
    
    async def send_request(self, api_request: ApiRequestDahua[T]) -> T:
        client = await self._get_http_client()
        
        http_request = api_request.generate_http_request()
        http_response = await client.send_request(http_request)
        
        if http_response.get_status_code() == HttpStatusCode.UNAUTHORIZED:
            nonce = ApiDahuaAuthenticationUtil.determine_nonce_from_http_response_unauthorized(http_response)
            realm = ApiDahuaAuthenticationUtil.determine_realm_from_http_response_unauthorized(http_response)

            http_request = self._add_header_authentication(http_request, nonce, realm)
            
            http_response = await client.send_request(http_request)
            
            if self._is_http_response_success(http_response):
                return self._parse_api_response(api_request, http_response)
            elif http_response.get_status_code() == HttpStatusCode.BAD_REQUEST:
                raise DahuaErrorBadRequest(self.ERROR_DAHUA_API.format(http_response=http_response))
            else:
                raise DahuaError(self.ERROR_DAHUA_API.format(http_response=http_response))
        else:
            raise DahuaError(self.ERROR_EXPECTED_DIGEST_CHALLENGE.format(status_code=http_response.get_status_code()))
        
    
    async def _get_http_client(self) -> PtcpHttpClient:
        if self._http_client is None:
            raise DahuaError(self.ERROR_NOT_CONNECTED)
        else:
            return self._http_client
        
    
    def _add_header_authentication(self, http_request: HttpRequest, nonce: Nonce, realm: str) -> HttpRequest:
        header_authentication = ApiDahuaAuthenticationUtil.generate_header_authentication(
            http_request,
            self._device,
            nonce,
            realm,
        )
        http_request.add_header(header_authentication)
        
        return http_request

        
    def _is_http_response_success(self, http_response: HttpResponse) -> bool:
        return http_response.get_status_code() in self._get_all_http_status_code_success()
    
        
    @staticmethod
    def _get_all_http_status_code_success() -> list[HttpStatusCode]:
        return [
            HttpStatusCode.OK,
        ]
    
    
    @staticmethod
    def _parse_api_response(api_request: ApiRequestDahua[T], http_response: HttpResponse) -> T:
        response_class = api_request.get_response_class()
        response_body_dict = ApiDahuaBodyParser.determine_dict(http_response)

        return response_class.parse(response_body_dict)
