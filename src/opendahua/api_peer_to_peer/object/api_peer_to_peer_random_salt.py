

class ApiPeerToPeerRandomSalt:
    def __init__(self, random_salt_string: str):
        self._random_salt_string: str = random_salt_string
        
    def get_random_salt_string(self) -> str:
        return self._random_salt_string
