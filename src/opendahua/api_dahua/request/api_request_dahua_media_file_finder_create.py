from typing import Type

from opendahua.api.api_request import T
from opendahua.api_dahua.request.api_request_dahua import ApiRequestDahua
from opendahua.api_dahua.response.api_response_dahua_media_file_finder_create import ApiResponseDahuaMediaFileFinderCreate
from opendahua.http.http_request_body import HttpRequestBody
from opendahua.http.http_request_method import HttpRequestMethod
from opendahua.object.url import Url


class ApiRequestDahuaMediaFileFinderCreate(ApiRequestDahua[ApiResponseDahuaMediaFileFinderCreate]):
    # Request constants.
    REQUEST_ENDPOINT = "/cgi-bin/mediaFileFind.cgi?action=factory.create"


    def determine_endpoint(self) -> Url:
        return Url(self.REQUEST_ENDPOINT)
    
    
    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.GET
    
    
    def determine_body_or_none(self) -> HttpRequestBody | None:
        return None
    
    
    def get_response_class(self) -> Type[T]:
        return ApiResponseDahuaMediaFileFinderCreate
