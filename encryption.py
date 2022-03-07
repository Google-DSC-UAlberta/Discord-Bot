import os
from dotenv import load_dotenv

# load the envionment variables from .env file
load_dotenv()

class Singleton():
    _instance = None

    # Making the class Singleton
    # make sure there is only one instance of the class
    def __new__(cls, *args, **kwargs):
        if Singleton._instance is None:
            Singleton._instance = object.__new__(cls, *args, **kwargs)
        return Singleton._instance

class Encryption(Singleton):
    # Constructor
    def __init__(self):
        self.key = int(os.getenv("KEY"))


    def encrypt_char(self, char):
        """
        Encrypts a single character

        Args: char: the character to be encrypted
        """
        return chr(ord('A') + (ord(char) - ord('A') + self.key) % 26)

    def encrypt(self, id):
        """
        Encrypts a id
        Args: id: the id to be encrypted
        """

        id = str(id)
        id = id.upper()
        cipher = ''
        for char in id:
            if char not in ' ,.':
                cipher += self.encrypt_char(char)
            else:
                cipher += char
        return cipher


    def decrypt_char(self, char):
        """
        Decrypts a single character

        Args: char: the character to be decrypted
        """
        return chr(ord('A') + (ord(char) - ord('A') + 26 - self.key) % 26)

    def decrypt(self, cipher):
        """
        Decrypts a id
        Args: cipher: the id to be decrypted
        """

        cipher = cipher.upper()
        id = ''
        for char in cipher:
            if char not in ' ,.':
                id += self.decrypt_char(char)
            else:
                id += char
        return id


