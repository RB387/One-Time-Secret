from Crypto.Cipher import AES
import base64


class Crypto:
    def __init__(self, key: str) -> None:
        key = self.append_bytes(12, key)
        self.cipher = AES.new(key, AES.MODE_ECB)

    def append_bytes(self, size: int, string: str) -> str:
        return b' ' * (size-(len(string) % size)) + bytes(string, 'utf-8')

    def encrypt(self, message: str) -> str:
        message = self.append_bytes(16, message)
        return base64.b64encode(self.cipher.encrypt(message))

    def decrypt(self, message: str) -> str:
        base64_decoded = base64.b64decode(message)
        decrypted = self.cipher.decrypt(base64_decoded)
        return decrypted.lstrip().decode('utf-8')
