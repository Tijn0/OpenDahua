import os

from src.logger import Logger
from src.object.dahua_device import DahuaDevice
from src.signaling_client import SignalingClient

SERIAL_NUMBER = os.getenv("SERIAL_NUMBER")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

def main() -> None:
    device = DahuaDevice(
        serial_number=SERIAL_NUMBER,
        username=USERNAME,
        password=PASSWORD,
    )
    signaling_client = SignalingClient(device)
    
    ptcp_socket = signaling_client.connect()
    
    ptcp_socket.send_bind(80)
    
    ptcp_socket.send(b"GET / HTTP/1.1\r\n\r\n")
    while True:
        try:
            response = ptcp_socket.recv(timeout=0.1)
            
            Logger.info(response)
        except TimeoutError:
            pass
    
if __name__ == '__main__':
    main()
