import json
import base64
from typing import Any
from Crypto.Cipher import AES
from django.conf import settings
from .wrapper import SingleInstance


@SingleInstance
class Cipher:
    def __init__(self, secret_key: bytes, use_base64=True, charset: str = 'UTF-8'):
        if isinstance(secret_key, str):
            self.secret_key = secret_key.encode(charset)
        else:
            self.secret_key = secret_key
        self.use_base64 = use_base64
        self.charset = charset

    def _padding_data(self, data: bytes):
        if len(data) % 16 != 0:
            data += b'\x00'
            while len(data) % 16 != 0:
                data += b'\x00'
        return data

    def _strip_padding_data(self, data: bytes):
        data = data.rstrip(b'\x00')
        return data

    def encrypt(self, data: Any):
        if isinstance(data, (dict, list)):
            data = json.dumps(data).encode(self.charset)
        elif not isinstance(data, bytes):
            data = str(data).encode(self.charset)
        encrypted_data = AES.new(self.secret_key, AES.MODE_ECB).encrypt(self._padding_data(data))
        if self.use_base64:
            encrypted_data = base64.b64encode(encrypted_data)
        return encrypted_data

    def decrypt(self, data: bytes, is_json: bool = False):
        if self.use_base64:
            data = base64.b64decode(data)
        decrypted_data = AES.new(self.secret_key, AES.MODE_ECB).decrypt(data)
        decrypted_data = self._strip_padding_data(decrypted_data)
        if is_json:
            decrypted_data = json.loads(decrypted_data)
        return decrypted_data


aes_cipher = Cipher(secret_key=settings.API_KEY)
