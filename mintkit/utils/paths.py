"""A custom path library.

"""

import os
import sys
import subprocess


class Path(str):
    def __init__(self, path):
        """An object for intelligently representing system paths.

        """
        super().__init__()
        self._path = os.path.abspath(path)

    def __add__(self, other):
        """Override add operator to combine with other path or string.

        """
        return Path(os.path.join(self._path, str(other)))

    def __getitem__(self, key):
        """Return a path sliced by a key.

        """
        split_path = self._path.split(os.sep)
        new_path = os.path.join(*split_path[key])
        return Path(new_path)

    def __len__(self):
        """Return the number of folders and files in the path.

        """
        return len(self._path.split(os.sep))

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
        components = self._path.split(os.sep)
        if len(components) == 0:
            raise ValueError('Invalid path.')
        # Adjust for strange behavior on Windows for drives
        if ':' in components[0]:
            components[0] = components[0] + os.sep
        # Get longest existing path
        curr_path = components.pop(0)
        while os.path.isdir(curr_path):
            curr_path = os.path.join(curr_path, components.pop(0))
        if len(components) >= max_depth:
            raise ValueError('Path creation would exceed maximum allowed depth.')
        os.mkdir(curr_path)
        while len(components) > 0:
            curr_path = os.path.join(curr_path, components.pop(0))
            os.mkdir(curr_path)

    def to_path(self):
        """Append to sys.path if not already present.

        """
        if self._path not in sys.path:
            sys.path.append(self._path)
