import logging

logger = logging.getLogger("fireworks")

_console_log_level: int = logging.INFO

_NAME_TO_LEVEL = {
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,
    "ERROR": logging.ERROR,
    "WARN": logging.WARNING,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def set_console_log_level(level: str) -> None:
    """
    Controls console logging.

    Args:
        level: the minimum level that prints out to console.
            Supported values: [CRITICAL, FATAL, ERROR, WARN,
            WARNING, INFO, DEBUG]
    """
    _console_log_level = _NAME_TO_LEVEL.get(level)
    if _console_log_level is None:
        raise ValueError(
            f"unrecognized log level {level}. Supported "
            f"values are {list(_NAME_TO_LEVEL.keys())}"
        )


def _log(message: str, level: int) -> None:
    """
    Logs message with a specific severity level.

    Args:
        message: the message to log,
        level: the severity level.
    """
    if _console_log_level >= level:
        print(message)
    logger.log(level, message)


def log_debug(message: str) -> None:
    _log(message, logging.DEBUG)


def log_info(message: str) -> None:
    _log(message, logging.INFO)


def log_warning(message: str) -> None:
    _log(message, logging.WARNING)


def log_error(message: str) -> None:
    _log(message, logging.ERROR)


def log_fatal(message: str) -> None:
    _log(message, logging.FATAL)


def log_critical(message: str) -> None:
    _log(message, logging.CRITICAL)
