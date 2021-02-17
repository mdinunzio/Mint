"""A custom path library.

"""
import os
import sys
import subprocess
import warnings


class Path(str):
    def __init__(self, path):
        """An object for intelligently representing system paths.

        """
        super().__init__()
        if isinstance(path, Path):
            self._path = os.path.normpath(path._path)
        elif isinstance(path, str):
            self._path = os.path.normpath(path)

    def split(self):
        """Return a list of strings of Path components.

        """
        components = self._path.split(os.sep)
        cleaned = [x if ':' not in x else x + os.sep for x in components]
        return cleaned

    def join(self, *args):
        """Return a Path joined with other strings or Paths.

        """
        return Path(os.path.join(self._path, *args))

    def __add__(self, other):
        """Override add operator to combine with other path or string.

        """
        return self.join(str(other))

    def __getitem__(self, key):
        """Return a path sliced by a key.

        """
        split_path = self.split()
        if isinstance(key, int):
            return Path(split_path[key])
        return Path(os.path.join(*split_path[key]))

    def __len__(self):
        """Return the number of folders and files in the path.

        """
        return len(self.split())

    def __str__(self):
        """Represent as a string.

        """
        return self._path

    def __repr__(self):
        """"Represent in console.

        """
        return self._path

    def open(self):
        """Open in Windows explorer.

        """
        if not os.path.exists(self._path):
            raise ValueError('Path does not exist.')
        subprocess.run(['explorer', self._path])

    def parent(self):
        """Return parent directory.

        """
        return self + '..'

    def exists(self):
        """Return whether the path exists.

        """
        return os.path.exists(self._path)

    def create(self, max_depth=5):
        """Create the path if it is a directory and does not exist.
        If more than max_depth folders need to be created the
        creation process will be aborted.

        """
        if os.path.exists(self._path):
            raise ValueError('Path already exists.')
        components = self.split()
        if len(components) == 0:
            raise ValueError('Invalid path.')
        # Get longest existing path
        curr_path = Path(components.pop(0))
        while os.path.isdir(curr_path):
            curr_path = curr_path + components.pop(0)
        if len(components) >= max_depth:
            raise ValueError(
                'Path creation would exceed maximum allowed depth.')
        os.mkdir(curr_path)
        while len(components) > 0:
            curr_path = curr_path + components.pop(0)
            os.mkdir(curr_path)

    def append_to_syspath(self):
        """Append to sys.path if not already present.

        """
        if self._path not in sys.path:
            sys.path.append(self._path)

    def save(self, file_path):
        """Save to a text file.

        """
        with open(file_path, 'w') as file:
            file.write(self._path)


class PathManager:
    def __init__(self):
        """A class for managing multiple Path objects.

        """
        self.__dict__['_paths'] = dict()

    def __getattr__(self, item):
        """Get the path using dot notation.

        """
        return self._paths[item]

    def __setattr__(self, key, value):
        """Set the path using dot notation.

        """
        if isinstance(value, Path):
            self._paths[key] = value
        else:
            self._paths[key] = Path(value)

    def __str__(self):
        """Represent as a string.

        """
        ret = 'Paths:'
        for path in self._paths:
            ret += f'\n{path}: {self._paths[path]}'
        return ret

    def __repr__(self):
        """Represent in the console.

        """
        return str(self)


def from_file(file_path):
    """Return a Path from a saved file.

    """
    with open(file_path, 'r') as file:
        path_str = file.read()
    return Path(path_str)


def create_key_paths(paths):
    """Ensure paths important to program function exist.

    """
    # appdata
    if not paths.appdata.exists():
        paths.appdata.create()
    # logs
    if not paths.logs.exists():
        paths.logs.create()
    # settings
    if not paths.settings.exists():
        paths.settings.create()
    # creds
    if not paths.creds.exists():
        paths.creds.create()
    # plots
    if not paths.plots.exists():
        paths.plots.create()


def setup_template_path(paths):
    """Configure the path to the Excel template (Cash Flow) file.

    """
    print('Please enter the full path to the template file.')
    template_path = input('template path: ')
    template_path = Path(template_path)
    template_path.save(paths.settings + 'template.path')


def get_template_path(paths):
    """Return the template path saved in the user's settings. Otherwise
    create it.

    """
    saved_template_path = paths.settings + 'template.path'
    if saved_template_path.exists():
        template_path = from_file(saved_template_path)
    else:
        warnings.warn('Template path is not saved, reverting to default.')
        template_path = paths.home + 'Google Drive/Finances/Cash Flow.xlsm'
    return template_path
