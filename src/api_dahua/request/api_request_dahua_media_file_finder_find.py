from typing import Type
from datetime import datetime

from src.api.api_request import T
from src.api_dahua.object.api_dahua_media_file_finder_identifier import ApiDahuaMediaFileFinderIdentifier
from src.api_dahua.request.api_request_dahua import ApiRequestDahua
from src.api_dahua.response.api_response_dahua_media_file_finder_find import ApiResponseDahuaMediaFileFinderFind
from src.http.http_request_body import HttpRequestBody
from src.http.http_request_method import HttpRequestMethod
from src.object.url import Url


class ApiRequestDahuaMediaFileFinderFind(ApiRequestDahua[ApiResponseDahuaMediaFileFinderFind]):
    # Request constants.
    REQUEST_ENDPOINT = "/cgi-bin/mediaFileFind.cgi?action=findFile&object={media_file_finder_identifier}&condition.Channel={channel_identifier}&condition.StartTimeRealUTC={time_start}&condition.EndTimeRealUTC={time_end}"
    
    
    def __init__(
            self,
            media_file_finder_identifier: ApiDahuaMediaFileFinderIdentifier,
            channel_identifier: int,
            time_start: datetime,
            time_end: datetime,
    ):
        self._media_file_finder_identifier: ApiDahuaMediaFileFinderIdentifier = media_file_finder_identifier
        self._channel_identifier: int = channel_identifier
        self._time_start: datetime = time_start
        self._time_end: datetime = time_end
        
        
    def determine_endpoint(self) -> Url:
        return Url(
            self.REQUEST_ENDPOINT.format(
                media_file_finder_identifier = self._media_file_finder_identifier.get_media_file_identifier_int(),
                channel_identifier = self._channel_identifier,
                time_start = self._time_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                time_end = self._time_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            ),
        )
    
    
    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.GET
    
    
    def determine_body_or_none(self) -> HttpRequestBody | None:
        return None
    
    
    def get_response_class(self) -> Type[T]:
        return ApiResponseDahuaMediaFileFinderFind
    