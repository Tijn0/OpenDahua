from typing import Type

from opendahua.api.api_request import T
from opendahua.api_dahua.object.api_dahua_media_file_finder_identifier import ApiDahuaMediaFileFinderIdentifier
from opendahua.api_dahua.request.api_request_dahua import ApiRequestDahua
from opendahua.api_dahua.response.api_response_dahua_media_file_finder_read import ApiResponseDahuaMediaFileFinderRead
from opendahua.http.http_request_body import HttpRequestBody
from opendahua.http.http_request_method import HttpRequestMethod
from opendahua.object.url import Url


class ApiRequestDahuaMediaFileFinderRead(ApiRequestDahua[ApiResponseDahuaMediaFileFinderRead]):
    # Request constants.
    REQUEST_ENDPOINT = "/cgi-bin/mediaFileFind.cgi?action=findNextFile&object={media_file_finder_identifier}&count={number_of_result_maximum}"
    
    def __init__(self, media_file_finder_identifier: ApiDahuaMediaFileFinderIdentifier, number_of_result_maximum: int) -> None:
        self._media_file_finder_identifier: ApiDahuaMediaFileFinderIdentifier = media_file_finder_identifier
        self._number_of_result_maximum: int = number_of_result_maximum


    def determine_endpoint(self) -> Url:
        return Url(
            self.REQUEST_ENDPOINT.format(
                media_file_finder_identifier = self._media_file_finder_identifier,
                number_of_result_maximum = self._number_of_result_maximum,
            ),
        )


    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.GET


    def determine_body_or_none(self) -> HttpRequestBody | None:
        return None


    def get_response_class(self) -> Type[T]:
        return ApiResponseDahuaMediaFileFinderRead
