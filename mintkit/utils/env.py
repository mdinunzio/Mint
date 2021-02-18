import mintkit.config as cfg
import mintkit.utils.logging
import os
import psutil
import ctypes
import sys
import subprocess


log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)


def get_username():
    """Return the OS username.

    """
    return os.path.expanduser('~').split(os.sep)[-1].lower()


def taskkill(image_name):
    """Kill a task with the given image name.

    """
    procs = [x for x in psutil.process_iter() if image_name in x.name()]
    for p in procs:
        p.kill()


def get_chrome_version():
    """Return the version of Chrome on this PC.

    """
    cmd = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" ' \
          r'/v version'
    res = subprocess.run(cmd, capture_output=True)
    version = res.stdout.decode('utf-8')
    version = version.split(' ')[-1]
    version = version.strip()
    return version


def request_uac(task):
    """Run the given task after requesting UAC permissions.

    """
    params = str(cfg.paths.app + 'run.py') + f' --task {task}'
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1)
