from typing import Type

from src.api.api_request import T
from src.api_dahua.request.api_request_dahua import ApiRequestDahua
from src.api_dahua.response.api_response_dahua_media_file_download import ApiResponseDahuaMediaFileDownload
from src.http.http_request_body import HttpRequestBody
from src.http.http_request_method import HttpRequestMethod
from src.object.url import Url


class ApiRequestDahuaMediaFileDownload(ApiRequestDahua[ApiResponseDahuaMediaFileDownload]):
    # Request constants.
    REQUEST_ENDPOINT = "/cgi-bin/RPC_Loadfile/{path}"
    
    
    def __init__(self, path: str):
        self._path: str = path
    
    
    def determine_endpoint(self) -> Url:
        return Url(self.REQUEST_ENDPOINT.format(path=self._path))
    
    
    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.GET
    
    
    def determine_body_or_none(self) -> HttpRequestBody | None:
        return None
    
    
    def get_response_class(self) -> Type[T]:
        return ApiResponseDahuaMediaFileDownload

