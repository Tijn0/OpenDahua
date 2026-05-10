from typing import Type

from src.api.api_request import T
from src.api_dahua.object.api_dahua_media_file_finder_identifier import ApiDahuaMediaFileFinderIdentifier
from src.api_dahua.request.api_request_dahua import ApiRequestDahua
from src.api_dahua.response.api_response_dahua_media_file_finder_close import ApiResponseDahuaMediaFileFinderClose
from src.http.http_request_body import HttpRequestBody
from src.http.http_request_method import HttpRequestMethod
from src.object.url import Url


class ApiRequestDahuaMediaFileFinderClose(ApiRequestDahua[ApiResponseDahuaMediaFileFinderClose]):
    # Request constants.
    REQUEST_ENDPOINT = "/cgi-bin/mediaFileFind.cgi?action=destroy&object={media_file_finder_identifier}"
    
    
    def __init__(self, media_file_finder_identifier: ApiDahuaMediaFileFinderIdentifier):
        self._media_file_finder_identifier: ApiDahuaMediaFileFinderIdentifier = media_file_finder_identifier
    
    
    def determine_endpoint(self) -> Url:
        return Url(
            self.REQUEST_ENDPOINT.format(
                media_file_finder_identifier = self._media_file_finder_identifier.get_media_file_identifier_int()
            ),
        )
    
    
    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.GET
    
    
    def determine_body_or_none(self) -> HttpRequestBody | None:
        return None
    
    
    def get_response_class(self) -> Type[T]:
        return ApiResponseDahuaMediaFileFinderClose
    