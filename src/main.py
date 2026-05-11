import asyncio
from datetime import datetime, timedelta
import os

from src.dahua.dahua_nvr import DahuaNVR

SERIAL_NUMBER = os.getenv("SERIAL_NUMBER")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

async def main() -> None:
    async with DahuaNVR(SERIAL_NUMBER, USERNAME, PASSWORD) as nvr:
        all_video = await nvr.get_all_video(
            channel=2,
            time_start=datetime.now() - timedelta(hours=1),
            time_end=datetime.now(),
        )
        
        for video in all_video:
            await nvr.download_video(video)
        
if __name__ == '__main__':
    asyncio.run(main())
