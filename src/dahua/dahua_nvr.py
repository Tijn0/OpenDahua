from datetime import datetime
from pathlib import Path

import aiofiles

from src.api_dahua.api_client_dahua import ApiClientDahua
from src.api_dahua.object.api_dahua_video_stream import ApiDahuaVideoStream
from src.api_dahua.request.api_request_dahua_machine_name_read import ApiRequestDahuaMachineNameRead
from src.api_dahua.request.api_request_dahua_media_file_download import ApiRequestDahuaMediaFileDownload
from src.api_dahua.request.api_request_dahua_media_file_finder_close import ApiRequestDahuaMediaFileFinderClose
from src.api_dahua.request.api_request_dahua_media_file_finder_create import ApiRequestDahuaMediaFileFinderCreate
from src.api_dahua.request.api_request_dahua_media_file_finder_find import ApiRequestDahuaMediaFileFinderFind
from src.api_dahua.request.api_request_dahua_media_file_finder_read import ApiRequestDahuaMediaFileFinderRead
from src.api_dahua.request.api_request_dahua_time_current_read import ApiRequestDahuaTimeCurrentRead
from src.dahua.dahua_device import DahuaDevice
from src.dahua.object.dahua_video import DahuaVideo


class DahuaNVR:
    # Number constants.
    NUMBER_OF_MEDIA_FILE_FIND_RESULT_MAXIMUM = 100
    
    # Format constants.
    FORMAT_FILENAME_VIDEO = "{name_nvr}_ch{channel_number}_{time_start:%Y%m%d%H%M%S}_{time_end:%Y%m%d%H%M%S}.{filetype}"
    
    # File constants.
    FILE_MODE_WRITE_BYTES = "wb"

    def __init__(self, serial_number: str, username: str, password: str):
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


    # TODO: return type
    async def get_all_video(self, channel: int, time_start: datetime, time_end: datetime) -> list[DahuaVideo]:
        response_media_file_finder_create = await self._client.send_request(ApiRequestDahuaMediaFileFinderCreate())
        media_file_finder_identifier = response_media_file_finder_create.get_media_file_finder_identifier()
        
        request_media_file_finder_find = ApiRequestDahuaMediaFileFinderFind(
            media_file_finder_identifier=media_file_finder_identifier,
            channel_identifier=channel,
            time_start=time_start,
            time_end=time_end,
        )
        await self._client.send_request(request_media_file_finder_find)
        
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
        
        
    async def download_video(self, video: DahuaVideo) -> Path:
        response_video_download = await self._client.send_request(
            ApiRequestDahuaMediaFileDownload(video.get_path_file_remote()),
        )
        
        filename_video = await self._generate_filename_video(video)
        
        # TODO: magic number
        async with aiofiles.open(filename_video, "wb") as file:
            await file.write(response_video_download.get_media_file_bytes())
            
        return Path(filename_video)
        
        
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
