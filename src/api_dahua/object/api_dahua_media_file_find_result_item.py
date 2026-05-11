from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.api_dahua.object.api_dahua_video_stream import ApiDahuaVideoStream


@dataclass(frozen=True)
class ApiDahuaMediaFileFindResultItem:
    _channel: int
    _time_start: datetime
    _time_end: datetime
    _path_file: Path
    _file_type: str
    _video_stream: ApiDahuaVideoStream

    def get_channel_int(self) -> int:
        return self._channel
    
    
    def get_time_start(self) -> datetime:
        return self._time_start
    

    def get_time_end(self) -> datetime:
        return self._time_end
    

    def get_path_file(self) -> Path:
        return self._path_file
    
    
    def get_file_type(self) -> str:
        return self._file_type

    def get_video_stream(self) -> ApiDahuaVideoStream:
        return self._video_stream
