from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from opendahua.api_dahua.object.api_dahua_media_file_find_result_item import ApiDahuaMediaFileFindResultItem
from opendahua.dahua.object.dahua_video_file_type import DahuaVideoFileType


@dataclass(frozen=True)
class DahuaVideo:
    _channel_int: int
    _time_start: datetime
    _time_end: datetime
    _path_file_remote: Path
    _file_type: DahuaVideoFileType
    
    @classmethod
    def create_from_media_file_find_result_item(cls, media_file_find_result_item: ApiDahuaMediaFileFindResultItem) -> DahuaVideo:
        return cls(
            _channel_int = media_file_find_result_item.get_channel_int(),
            _time_start = media_file_find_result_item.get_time_start(),
            _time_end = media_file_find_result_item.get_time_end(),
            _path_file_remote = media_file_find_result_item.get_path_file(),
            _file_type = DahuaVideoFileType(media_file_find_result_item.get_file_type()),
        )
    
    
    def get_channel_int(self) -> int:
        return self._channel_int
    
        
    def get_time_start(self) -> datetime:
        return self._time_start
    
    
    def get_time_end(self) -> datetime:
        return self._time_end


    def get_path_file_remote(self) -> Path:
        return self._path_file_remote
    
    def get_file_type(self) -> DahuaVideoFileType:
        return self._file_type
