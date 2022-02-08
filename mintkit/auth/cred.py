import mintkit.settings as cfg
import mintkit.utils.logs
import mintkit.auth.secret
import json


log = mintkit.utils.logs.get_logger(cfg.PROJECT_NAME)


class Credential:
    def __init__(self, name):
        """A class for managing credentials.

        """
        self.__dict__['name'] = name
        self.__dict__['_data'] = dict()

    def __getattr__(self, item):
        """Get the credential component using dot notation.

        """
        return self._data[item]

    def __setattr__(self, key, value):
        """Set the credential component dot notation.

        """
        self._data[key] = value

    def __str__(self):
        """Represent as a string.

        """
        ret = f'Credentials for {self.name}:\n'
        for item in self._data:
            ret += f'\n{item}: {self._data[item]}'
        return ret

    def __repr__(self):
        """Represent in the console.

        """
        return str(self)

    def to_json(self):
        """Return the json representation of the credentials.

        """
        return json.dumps(self._data)

    def save(self, key, directory=None):
        """Save the credential as a secret.

        """
        if directory is None:
            directory = cfg.paths.creds
        secret = mintkit.auth.secret.Secret(name=self.name,
                                            plaintext=self.to_json())
        secret.encrypt(key)
        secret.save(name=self.name, directory=directory)


def from_file(name, key, directory=None):
    """Load credentials from a file.

    """
    if directory is None:
        directory = cfg.paths.creds
    secret = mintkit.auth.secret.from_file(name=name, directory=directory)
    secret.decrypt(key)
    data = json.loads(secret.plaintext)
    credential = Credential(name)
    for item in data:
        setattr(credential, item, data[item])
    return credential

