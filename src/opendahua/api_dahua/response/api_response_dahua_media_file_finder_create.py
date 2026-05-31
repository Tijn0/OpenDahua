from dataclasses import dataclass

from opendahua.api.api_response import ApiResponse
from opendahua.api_dahua.object.api_dahua_media_file_finder_identifier import ApiDahuaMediaFileFinderIdentifier
from opendahua.api_dahua.response.api_response_dahua import ApiResponseDahua


@dataclass(frozen=True)
class ApiResponseDahuaMediaFileFinderCreate(ApiResponseDahua):
    # Field constants.
    FIELD_IDENTIFIER_MEDIA_FILE_FINDER = "result"
    
    _media_file_finder_identifier: ApiDahuaMediaFileFinderIdentifier
    

    @classmethod
    def parse(cls, value: dict) -> ApiResponse:
        identifier_media_file_finder = ApiDahuaMediaFileFinderIdentifier(int(value[cls.FIELD_IDENTIFIER_MEDIA_FILE_FINDER]))
        
        return cls(identifier_media_file_finder)
    
    def get_media_file_finder_identifier(self) -> ApiDahuaMediaFileFinderIdentifier:
        return self._media_file_finder_identifier
