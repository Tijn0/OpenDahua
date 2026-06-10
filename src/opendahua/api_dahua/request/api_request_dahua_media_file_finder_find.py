from datetime import datetime
from typing import Type
import urllib.parse

from opendahua.api.api_request import T
from opendahua.api_dahua.object.api_dahua_media_file_finder_identifier import ApiDahuaMediaFileFinderIdentifier
from opendahua.api_dahua.request.api_request_dahua import ApiRequestDahua
from opendahua.api_dahua.response.api_response_dahua_media_file_finder_find import ApiResponseDahuaMediaFileFinderFind
from opendahua.http.http_request_body import HttpRequestBody
from opendahua.http.http_request_method import HttpRequestMethod
from opendahua.object.url import Url


class ApiRequestDahuaMediaFileFinderFind(ApiRequestDahua[ApiResponseDahuaMediaFileFinderFind]):
    # Request constants.
    REQUEST_ENDPOINT = "/cgi-bin/mediaFileFind.cgi?action=findFile&object={media_file_finder_identifier}&condition.Channel={channel_identifier}&condition.StartTime={time_start}&condition.EndTime={time_end}&condition.VideoStream=Main"
    
    def __init__(
            self,
            media_file_finder_identifier: ApiDahuaMediaFileFinderIdentifier,
            channel_identifier: int,
            time_start: datetime,
            time_end: datetime,
    ) -> None:
        self._media_file_finder_identifier: ApiDahuaMediaFileFinderIdentifier = media_file_finder_identifier
        self._channel_identifier: int = channel_identifier
        self._time_start: datetime = time_start
        self._time_end: datetime = time_end
        
        
    def determine_endpoint(self) -> Url:
        return Url(
            self.REQUEST_ENDPOINT.format(
                media_file_finder_identifier = self._media_file_finder_identifier.get_media_file_identifier_int(),
                channel_identifier = self._channel_identifier,
                time_start = urllib.parse.quote_plus(self._time_start.isoformat(sep=" ", timespec="seconds")),
                time_end = urllib.parse.quote_plus(self._time_end.isoformat(sep=" ", timespec="seconds")),
            ),
        )
    
    
    def get_request_method(self) -> HttpRequestMethod:
        return HttpRequestMethod.GET
    
    
    def determine_body_or_none(self) -> HttpRequestBody | None:
        return None
    
    
    def get_response_class(self) -> Type[T]:
        return ApiResponseDahuaMediaFileFinderFind
