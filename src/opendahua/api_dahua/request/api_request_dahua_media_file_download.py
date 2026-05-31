from pathlib import Path
from typing import Type

from opendahua.api.api_request import T
from opendahua.api_dahua.request.api_request_dahua import ApiRequestDahua
from opendahua.api_dahua.response.api_response_dahua_media_file_download import ApiResponseDahuaMediaFileDownload
from opendahua.http.http_request_body import HttpRequestBody
from opendahua.http.http_request_method import HttpRequestMethod
from opendahua.object.url import Url


class ApiRequestDahuaMediaFileDownload(ApiRequestDahua[ApiResponseDahuaMediaFileDownload]):
    # Request constants.
    REQUEST_ENDPOINT = "/cgi-bin/RPC_Loadfile/{path}"
    
    # Character constants.
    CHARACTER_LEADING_SLASH = "/"

    def __init__(self, path: Path):
        self._path: Path = path
    
    
    def determine_endpoint(self) -> Url:
        return Url(self.REQUEST_ENDPOINT.format(path=str(self._path).strip(self.CHARACTER_LEADING_SLASH)))
    
    
    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.GET
    
    
    def determine_body_or_none(self) -> HttpRequestBody | None:
        return None
    
    
    def get_response_class(self) -> Type[T]:
        return ApiResponseDahuaMediaFileDownload
