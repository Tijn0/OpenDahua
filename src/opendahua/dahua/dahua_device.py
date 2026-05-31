
class DahuaDevice:
    def __init__(self, serial_number: str, username: str, password: str) -> None:
        self._serial_number: str = serial_number
        self._username: str = username
        self._password: str = password
    
    def get_serial_number(self) -> str:
        return self._serial_number
    
    def get_username(self) -> str:
        return self._username
    
    def get_password(self) -> str:
        return self._password
