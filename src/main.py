import asyncio
import os

from src.api_dahua.api_client_dahua import ApiClientDahua
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

if __name__ == '__main__':
    asyncio.run(main())
