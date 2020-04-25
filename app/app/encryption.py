from Crypto.Cipher import AES
import base64


class Crypto:
    """
    A class used to encrypt and decrypt data

    ...

    Attributes
    ----------
    cipher : Crypto.Cipher._mode_ecb.EcbMode
        AES cipher with MODE_ENC and received key in __init__

    Methods
    -------
    encrypt(message: str) -> str
        :returns string of encrypted with AES and coded with base64 message

    decrypt(message: str) -> str
        :returns string of decrypted with AES and decoded with base64 message
    """

    def __init__(self, key: str) -> None:
        '''
        :param key: Key to encrypt and decrypt data.
                    Key length must be less than 24 characters and more than 12
        '''
        key = self.__append_bytes(12, key)
        self.cipher = AES.new(key, AES.MODE_ECB)

    def __append_bytes(self, size: int, string: str) -> str:
        return b' ' * (size-(len(string) % size)) + bytes(string, 'utf-8')

    def encrypt(self, message: str) -> str:
        '''Encrypt message

        Encrypt message with AES and code it with base64

        :param message: The message that needs to be encrypted
        :return: string of encrypted with AES and coded with base64 message
        '''
        message = self.__append_bytes(16, message)
        return base64.b64encode(self.cipher.encrypt(message))

    def decrypt(self, message: str) -> str:
        '''Decrypt message

        Decrypt message with AES and code it with base64

        :param message: The message that needs to be decrypted
        :return: string of decrypted with AES and decoded with base64 message
        '''
        base64_decoded = base64.b64decode(message)
        decrypted = self.cipher.decrypt(base64_decoded)
        return decrypted.lstrip().decode('utf-8')
