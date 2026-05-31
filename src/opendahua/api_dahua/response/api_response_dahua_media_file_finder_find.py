from dataclasses import dataclass

from opendahua.api.api_response import ApiResponse
from opendahua.api_dahua.response.api_response_dahua import ApiResponseDahua


@dataclass(frozen=True)
class ApiResponseDahuaMediaFileFinderFind(ApiResponseDahua):
    @classmethod
    def parse(cls, value: dict) -> ApiResponse:
        pass
