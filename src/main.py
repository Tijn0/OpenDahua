from dahua_peer_to_peer_connection import DahuaPeerToPeerConnection
import os

from src.object.dahua_device import DahuaDevice

SERIAL_NUMBER = os.getenv("SERIAL_NUMBER")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

def main() -> None:
    device = DahuaDevice(
        serial_number=SERIAL_NUMBER,
        username=USERNAME,
        password=PASSWORD,
    )
    connection = DahuaPeerToPeerConnection(device)
    
    connection.connect()
    
if __name__ == '__main__':
    main()
