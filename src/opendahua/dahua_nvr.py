from datetime import datetime
from pathlib import Path
from typing import Literal

import aiofiles

from opendahua.api_dahua.api_client_dahua import ApiClientDahua
from opendahua.api_dahua.object.api_dahua_video_stream import ApiDahuaVideoStream
from opendahua.api_dahua.request.api_request_dahua_machine_name_read import ApiRequestDahuaMachineNameRead
from opendahua.api_dahua.request.api_request_dahua_media_file_download import ApiRequestDahuaMediaFileDownload
from opendahua.api_dahua.request.api_request_dahua_media_file_finder_close import ApiRequestDahuaMediaFileFinderClose
from opendahua.api_dahua.request.api_request_dahua_media_file_finder_create import ApiRequestDahuaMediaFileFinderCreate
from opendahua.api_dahua.request.api_request_dahua_media_file_finder_find import ApiRequestDahuaMediaFileFinderFind
from opendahua.api_dahua.request.api_request_dahua_media_file_finder_read import ApiRequestDahuaMediaFileFinderRead
from opendahua.api_dahua.request.api_request_dahua_time_current_read import ApiRequestDahuaTimeCurrentRead
from opendahua.common_object.dahua_error_bad_request import DahuaErrorBadRequest
from opendahua.dahua.dahua_device import DahuaDevice
from opendahua.dahua.object.dahua_video import DahuaVideo


class DahuaNVR:
    # Number constants.
    NUMBER_OF_MEDIA_FILE_FIND_RESULT_MAXIMUM = 100
    
    # Format constants.
    FORMAT_FILENAME_VIDEO = "{name_nvr}_ch{channel_number}_{time_start:%Y%m%d%H%M%S}_{time_end:%Y%m%d%H%M%S}.{filetype}"
    
    # File constants.
    FILE_MODE_WRITE_BYTES: Literal["wb"] = "wb"
    
    # Suffix constants.
    SUFFIX_PATH_DIRECTORY = "/"
    SUFFIX_EMPTY = ""

    def __init__(self, serial_number: str, username: str, password: str) -> None:
        self._device: DahuaDevice = DahuaDevice(serial_number, username, password)
        self._client: ApiClientDahua = ApiClientDahua(self._device)
        
        self._name: str|None = None
        
        
    async def connect(self) -> None:
        await self._client.connect()
    
    
    async def disconnect(self) -> None:
        await self._client.disconnect()
        
        
    async def get_name(self) -> str:
        if self._name is None:
            response = await self._client.send_request(ApiRequestDahuaMachineNameRead())
            self._name = response.get_name_string()
            
            return response.get_name_string()
        else:
            return self._name


    async def get_time(self) -> datetime:
        response = await self._client.send_request(ApiRequestDahuaTimeCurrentRead())
        
        return response.get_time_current()


    async def get_all_video(self, channel: int, time_start: datetime, time_end: datetime) -> list[DahuaVideo]:
        response_media_file_finder_create = await self._client.send_request(ApiRequestDahuaMediaFileFinderCreate())
        media_file_finder_identifier = response_media_file_finder_create.get_media_file_finder_identifier()
        
        request_media_file_finder_find = ApiRequestDahuaMediaFileFinderFind(
            media_file_finder_identifier=media_file_finder_identifier,
            channel_identifier=channel,
            time_start=time_start,
            time_end=time_end,
        )
        
        try:
            await self._client.send_request(request_media_file_finder_find)
        except DahuaErrorBadRequest:
            return []
            
        response_media_file_finder_read = await self._client.send_request(
            ApiRequestDahuaMediaFileFinderRead(
                media_file_finder_identifier,
                self.NUMBER_OF_MEDIA_FILE_FIND_RESULT_MAXIMUM,
            ),
        )
        
        all_result_item = response_media_file_finder_read.get_all_result_item()
        
        while len(response_media_file_finder_read.get_all_result_item()) == self.NUMBER_OF_MEDIA_FILE_FIND_RESULT_MAXIMUM:
            response_media_file_finder_read = await self._client.send_request(
                ApiRequestDahuaMediaFileFinderRead(
                    media_file_finder_identifier,
                    self.NUMBER_OF_MEDIA_FILE_FIND_RESULT_MAXIMUM,
                ),
            )
            all_result_item += response_media_file_finder_read.get_all_result_item()
            
        await self._client.send_request(ApiRequestDahuaMediaFileFinderClose(media_file_finder_identifier))
        
        all_video = []
        
        for result_item in all_result_item:
            if result_item.get_video_stream() == ApiDahuaVideoStream.MAIN:
                all_video.append(DahuaVideo.create_from_media_file_find_result_item(result_item))
            else:
                # Ignore.
                pass
            
        return all_video
        
        
    async def download_video(self, video: DahuaVideo, path: Path|str|None = None) -> Path:
        response_video_download = await self._client.send_request(
            ApiRequestDahuaMediaFileDownload(video.get_path_file_remote()),
        )
        
        if path is None:
            path_destination_video = Path(await self._generate_filename_video(video))
        else:
            path_destination_video = Path(path)
        
            if path_destination_video.is_dir() or str(path_destination_video).endswith(self.SUFFIX_PATH_DIRECTORY) or path_destination_video.suffix == self.SUFFIX_EMPTY:
                path_destination_video.mkdir(parents=True, exist_ok=True)
                
                path_destination_video = path_destination_video / await self._generate_filename_video(video)
            else:
                path_destination_video.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(path_destination_video, self.FILE_MODE_WRITE_BYTES) as file_video:
            await file_video.write(response_video_download.get_media_file_bytes())
            
        return path_destination_video
        
        
    async def _generate_filename_video(self, video: DahuaVideo) -> str:
        name_nvr = await self.get_name()
        
        return self.FORMAT_FILENAME_VIDEO.format(
            name_nvr=name_nvr,
            channel_number=video.get_channel_int(),
            time_start=video.get_time_start(),
            time_end=video.get_time_end(),
            filetype=video.get_file_type(),
        )

    async def __aenter__(self):
        await self.connect()
        
        return self
        
        
    async def __aexit__(self, *_):
        await self.disconnect()
