import base64
import hashlib
import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, CipherContext
from cryptography.hazmat.decrepit.ciphers import modes

from opendahua.common_object.key import Key
from opendahua.common_object.nonce import Nonce


class ApiPeerToPeerEncryptionUtil:
    # Name constants.
    NAME_HASH_KEY_DERIVED = "sha256"
    
    # Number constants.
    NUMBER_OF_ITERATION_KEY_DERIVED = 20_000
    
    # Length constants.
    LENGTH_KEY_DERIVED = 32
    
    # IV constants.
    IV = b"2z52*lk9o6HRyJrf"
    IV_DEVICE_INFO = b"MydvJw*Iw1w&i^kk"
    
    # Key constants.
    KEY_DEVICE_INFO = b"kRjmsUB&ezmdGLL67H#$ojw@XflcaIaf"
    
    @classmethod
    def encrypt(cls, key: Key, nonce: Nonce, data: str) -> str:
        encryptor = cls._generate_encryptor(key, nonce)
        
        data_encrypted = encryptor.update(data.encode()) + encryptor.finalize()
        
        return base64.b64encode(data_encrypted).decode()
    

    @classmethod
    def decrypt(cls, key: Key, nonce: Nonce, data: str) -> str:
        encryptor = cls._generate_encryptor(key, nonce)
        
        data_decrypted = encryptor.update(base64.b64decode(data)) + encryptor.finalize()
        
        return data_decrypted.decode()
    
   
    @classmethod
    def _generate_encryptor(cls, key: Key, nonce: Nonce) -> CipherContext:
        salt = nonce.get_nonce_string().encode()
        
        key_derived = hashlib.pbkdf2_hmac(
            hash_name=cls.NAME_HASH_KEY_DERIVED,
            password=key.get_key_bytes(),
            salt=salt,
            iterations=cls.NUMBER_OF_ITERATION_KEY_DERIVED,
            dklen=cls.LENGTH_KEY_DERIVED,
        )
        cipher = Cipher(algorithms.AES(key_derived), modes.OFB(cls.IV), backend=default_backend())
        
        return cipher.encryptor()
    
    
    @classmethod
    def decrypt_device_info(cls, device_info_encrypted: str) -> dict:
        key = Key(cls.KEY_DEVICE_INFO)
        
        cipher = Cipher(algorithms.AES(key.get_key_bytes()), modes.OFB(cls.IV_DEVICE_INFO), backend=default_backend())
        
        decryptor = cipher.decryptor()
        
        data_decrypted_bytes = decryptor.update(base64.b64decode(device_info_encrypted)) + decryptor.finalize()
        data_decrypted = json.loads(data_decrypted_bytes.decode())
        
        return data_decrypted
