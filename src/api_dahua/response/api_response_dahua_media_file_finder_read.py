from dataclasses import dataclass
from pathlib import Path

from src.api.api_response import ApiResponse
from src.api_dahua.object.api_dahua_media_file_find_result_item import ApiDahuaMediaFileFindResultItem
from src.api_dahua.object.api_dahua_video_stream import ApiDahuaVideoStream
from src.api_dahua.response.api_response_dahua import ApiResponseDahua


@dataclass(frozen=True)
class ApiResponseDahuaMediaFileFinderRead(ApiResponseDahua):
    _all_result_item: list[ApiDahuaMediaFileFindResultItem]
    
    # Field constants.
    FIELD_ALL_RESULT_ITEM = "items"
    FIELD_ITEM_CHANNEL = "Channel"
    FIELD_ITEM_TIME_START = "StartTime"
    FIELD_ITEM_TIME_END = "EndTime"
    FIELD_ITEM_PATH_FILE = "FilePath"
    FIELD_ITEM_FILE_TYPE = "Type"
    FIELD_ITEM_VIDEO_STREAM = "VideoStream"

    # Offset constants.
    OFFSET_CHANNEL_INDEX_TO_NUMBER = 1

    @classmethod
    def parse(cls, value: dict) -> ApiResponse:
        all_result_item = []
        
        for result_item_dict in value.get(cls.FIELD_ALL_RESULT_ITEM, []):
            all_result_item.append(
                ApiDahuaMediaFileFindResultItem(
                    _channel=result_item_dict[cls.FIELD_ITEM_CHANNEL] + cls.OFFSET_CHANNEL_INDEX_TO_NUMBER,
                    _time_start=result_item_dict[cls.FIELD_ITEM_TIME_START],
                    _time_end=result_item_dict[cls.FIELD_ITEM_TIME_END],
                    _path_file=Path(result_item_dict[cls.FIELD_ITEM_PATH_FILE]),
                    _file_type=result_item_dict[cls.FIELD_ITEM_FILE_TYPE],
                    _video_stream=ApiDahuaVideoStream(result_item_dict[cls.FIELD_ITEM_VIDEO_STREAM]),
                ),
            )
        
        return cls(all_result_item)

    def get_all_result_item(self) -> list[ApiDahuaMediaFileFindResultItem]:
        return self._all_result_item
