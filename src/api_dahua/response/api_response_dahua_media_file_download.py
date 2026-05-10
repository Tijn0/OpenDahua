from dataclasses import dataclass

from src.api.api_response import ApiResponse
from src.api_dahua.response.api_response_dahua import ApiResponseDahua


@dataclass(frozen=True)
class ApiResponseDahuaMediaFileDownload(ApiResponseDahua):
    # Field constants.
    FIELD_MEDIA_FILE_BYTES = "data"
    
    _media_file_bytes: bytes
    
    @classmethod
    def parse(cls, value: dict) -> ApiResponse:
        media_file_bytes = value[cls.FIELD_MEDIA_FILE_BYTES]
        
        return cls(media_file_bytes)
    
    
    def get_media_file_bytes(self) -> bytes:
        return self._media_file_bytes
    