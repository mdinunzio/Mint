import mintkit.settings as cfg
import mintkit.utils.logs
import mintkit.utils.paths
import Crypto.Cipher.AES
import hashlib
import pickle


log = mintkit.utils.logs.get_logger(cfg.PROJECT_NAME)


class Secret:
    def __init__(self, name, plaintext):
        """A class to save and protect client secrets.

        """
        self.name = name
        self.plaintext = plaintext
        self.encrypted = False
        self.nonce = b''
        self.ciphertext = b''
        self.tag = b''

    def encrypt(self, key):
        """Encrypt the data.

        """
        key = key.encode('utf-8')
        hash_ = hashlib.md5(key).digest()
        plaintext = self.plaintext.encode('utf-8')
        cipher = Crypto.Cipher.AES.new(hash_, Crypto.Cipher.AES.MODE_EAX)
        self.ciphertext, self.tag = cipher.encrypt_and_digest(plaintext)
        self.nonce = cipher.nonce
        self.plaintext = ''
        self.encrypted = True

    def decrypt(self, key):
        """Decrypt the data.

        """
        key = key.encode('utf-8')
        hash_ = hashlib.md5(key).digest()
        cipher = Crypto.Cipher.AES.new(
            key=hash_, mode=Crypto.Cipher.AES.MODE_EAX, nonce=self.nonce)
        plaintext = cipher.decrypt(self.ciphertext)
        cipher.verify(self.tag)
        self.plaintext = plaintext.decode('utf-8')
        self.nonce = b''
        self.ciphertext = b''
        self.tag = b''
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

    def __str__(self):
        """Represent as a string.

        """
        return f'Secret: {self.name}'

    def __repr__(self):
        """Represent in the console.

        """
        ret = f'Secret: {self.name}'
        if self.encrypted:
            ret += ' (encrypted)'
        else:
            ret += ' (decrypted)\n'
            ret += f'Plaintext:\n{self.plaintext}'
        return ret


def from_file(name=None, directory=None):
    """Load a secret from a file.

    """
    if name is not None:
        directory = cfg.paths.creds + f'{name}.sec'
    elif directory is None:
        raise ValueError('Must pass either name or directory parameter.')
    with open(directory, 'rb') as file:
        secret = pickle.load(file)
    return secret
