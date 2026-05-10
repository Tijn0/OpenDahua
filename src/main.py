import asyncio
import os
import time
from datetime import datetime, timedelta

from src.api_dahua.api_client_dahua import ApiClientDahua
from src.api_dahua.request.api_request_dahua_media_file_download import ApiRequestDahuaMediaFileDownload
from src.api_dahua.request.api_request_dahua_media_file_finder_close import ApiRequestDahuaMediaFileFinderClose
from src.api_dahua.request.api_request_dahua_media_file_finder_create import ApiRequestDahuaMediaFileFinderCreate
from src.api_dahua.request.api_request_dahua_media_file_finder_find import ApiRequestDahuaMediaFileFinderFind
from src.api_dahua.request.api_request_dahua_media_file_finder_read import ApiRequestDahuaMediaFileFinderRead
from src.api_dahua.request.api_request_dahua_time_current_read import ApiRequestDahuaTimeCurrentRead
from src.dahua.dahua_device import DahuaDevice

SERIAL_NUMBER = os.getenv("SERIAL_NUMBER")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

async def main() -> None:
    device = DahuaDevice(
        serial_number=SERIAL_NUMBER,
        username=USERNAME,
        password=PASSWORD,
    )

    dahua_client = ApiClientDahua(device)
    request = ApiRequestDahuaTimeCurrentRead()

    response = await dahua_client.send_request(request)
    response = await dahua_client.send_request(request)

    print(response.get_time_current().year)


    request = ApiRequestDahuaMediaFileFinderCreate()
    response = await dahua_client.send_request(request)
    media_file_finder_identifier = response.get_media_file_finder_identifier()
    print(response.get_media_file_finder_identifier().get_media_file_identifier_int())

    request = ApiRequestDahuaMediaFileFinderFind(
        media_file_finder_identifier,
        1,
        datetime.now() - timedelta(days=9),
        datetime.now(),
    )
    await dahua_client.send_request(request)

    request = ApiRequestDahuaMediaFileFinderRead(media_file_finder_identifier)
    response = await dahua_client.send_request(request)
    
    request = ApiRequestDahuaMediaFileFinderClose(media_file_finder_identifier)
    await dahua_client.send_request(request)
    

if __name__ == '__main__':
    asyncio.run(main())
