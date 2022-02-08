import logging
import sys
import os
import datetime
import traceback
import warnings


# setup
logging.getLogger().setLevel(logging.NOTSET)

_log_settings = {'default_logger': None,
                 'logging_directory': '',
                 'debug_mode': False,
                 'email': False}
_loggers = dict()


def _excepthook_custom(exc_type, exc_value, traceback_):
    """Use to replace sys.excepthook.

    """
    _log_settings['default_logger'].error(
        'uncaught exception',
        exc_info=(exc_type, exc_value, traceback_)
    )


def _showwarning_custom(message, category, filename, lineno, file=None,
                        line=None):
    """Use to replace warnings.showwarning.

    """
    msg = warnings.WarningMessage(message, category, filename,
                                  lineno, file, line)
    text = warnings._formatwarnmsg_impl(msg)
    _log_settings['default_logger'].warn(text)


def set_logging_directory(log_path):
    """Set the log path for the project.

    """
    _log_settings['logging_directory'] = str(log_path)


def set_debug_mode(debug_mode):
    """Set the logger debug mode.

    """
    _log_settings['debug_mode'] = debug_mode


def set_default_logger(logger):
    """Set the default logger class.

    """
    _log_settings['default_logger'] = logger
    sys.excepthook = _excepthook_custom


def get_username():
    """Return the OS username.

    """
    home_dir = os.path.expanduser('~')
    username = home_dir.split(os.sep)[-1]
    return username


def _setup_logger(logger_name):
    """Setup a new logger.

    """
    # Create a custom loggers
    logger = logging.getLogger(logger_name)

    # Create handlers
    today = datetime.date.today()
    fl_nm = f'{get_username()}_'
    fl_nm += f'{today:%Y%m%d}'
    if _log_settings['debug_mode']:
        fl_nm += '_debug'
    fl_nm += '.log'
    fl_path = os.path.join(_log_settings['logging_directory'], fl_nm)
    fl_handler = logging.FileHandler(fl_path)
    fl_handler.setLevel(logging.INFO)
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.INFO)

    # Create formatters
    fl_template = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    fl_formatter = logging.Formatter(fl_template)
    fl_handler.setFormatter(fl_formatter)
    c_template = '%(message)s'
    c_formatter = logging.Formatter(c_template)
    c_handler.setFormatter(c_formatter)

    # Add handlers to the logger
    logger.addHandler(fl_handler)
    logger.addHandler(c_handler)

    logger.info(f'Logger "{logger_name}" initialized.')

    # Add to loggers
    _loggers[logger_name] = logger
    if _log_settings['default_logger'] is None:
        set_default_logger(logger)

    return logger


def get_logger(logger_name):
    """Return a logger.

    """
    if logger_name not in _loggers:
        return _setup_logger(logger_name)
    else:
        return _loggers[logger_name]
