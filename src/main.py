import asyncio
import os

from src.dahua.dahua_device import DahuaDevice
from src.http.http_request import HttpRequest
from src.http.http_request_method import HttpRequestMethod
from src.object.url import Url
from src.ptcp.ptcp_http_client import PtcpHttpClient
from src.signaling_client import SignalingClient

SERIAL_NUMBER = os.getenv("SERIAL_NUMBER")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

async def main() -> None:
    device = DahuaDevice(
        serial_number=SERIAL_NUMBER,
        username=USERNAME,
        password=PASSWORD,
    )
    signaling_client = SignalingClient(device)
    
    ptcp_socket = await signaling_client.connect()
    
    await ptcp_socket.start()

    request = HttpRequest(HttpRequestMethod.GET, Url("/cgi-bin/mediaFileFind.cgi?action=findFile"))
    # request = HttpRequest(HttpRequestMethod.GET, Url("/"))

    http_client = PtcpHttpClient(ptcp_socket)
    
    response = await http_client.send_request_and_receive_response(request)
    
    print(response.get_all_header())
    print(response.get_status_code())
    print(response.get_body_or_none())

    while True:
        await ptcp_socket.receive()
    
if __name__ == '__main__':
    asyncio.run(main())
