import mintkit.config as cfg
import mintkit.utils.logging
import mintkit.utils.paths
import Crypto.Cipher.AES
import json
import pickle


log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)


def load_secret(name=None, secret_path=None):
    """Load a secret from a file.

    """
    if name is not None:
        secret_path = cfg.paths.creds + f'{name}.sec'
    elif secret_path is None:
        raise ValueError('Must pass either name or secret_path parameter.')
    with open(secret_path, 'rb') as file:
        secret = pickle.load(file)
    return secret


class Secret:
    def __init__(self, name, plaintext):
        """A class to save and protect client secrets.

        """
        self.name = name
        self.plaintext = plaintext
        self.encrypted = False
        self.nonce = b''
        self.ciphertext = b''

    def encrypt(self, key):
        """Encrypt the data.

        """
        key = key.encode('utf-8')
        plaintext = self.plaintext.encode('utf-8')
        cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_EAX)
        self.ciphertext = cipher.encrypt_and_digest(plaintext)
        self.nonce = cipher.nonce
        self.plaintext = ''
        self.encrypted = True

    def decrypt(self, key):
        """Decrypt the data.

        """
        key = key.encode('utf-8')
        cipher = Crypto.Cipher.AES.new(
            key=key, mode=Crypto.Cipher.AES.MODE_EAX, nonce=self.nonce)
        plaintext = cipher.decrypt(self.ciphertext)
        self.plaintext = plaintext.decode('utf-8')
        self.nonce = b''
        self.ciphertext = b''
        self.encrypted = False

    def save(self, name=None, directory=None):
        """Save the current secret.

        """
        if not self.encrypted:
            raise ValueError('Cannot save unencrypted secret')
        if name is None:
            name = self.name
        if directory is None:
            directory = cfg.paths.creds
        else:
            directory = mintkit.utils.paths.Path(directory)
        path = directory + f'{name}.sec'
        with open(path, 'wb') as file:
            pickle.dump(self, file)

