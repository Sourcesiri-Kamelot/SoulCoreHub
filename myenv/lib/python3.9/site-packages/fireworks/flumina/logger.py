import copy
import logging
import os
import sys
import uvicorn
import queue
import atexit

# ANSI escape sequences for different log levels
COLORS = {
    "WARNING": "\033[93m",  # Yellow
    "INFO": "\033[94m",  # Blue
    "DEBUG": "\033[92m",  # Green
    "CRITICAL": "\033[91m",  # Red
    "ERROR": "\033[91m",  # Red
    "RESET": "\033[0m",  # Reset to default
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        # Format string with levelname and message
        log_fmt = f"%(asctime)s {COLORS['DEBUG']}Flumina: {COLORS[record.levelname]}%(message)s{COLORS['RESET']}"
        # ISO8601 format
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%dT%H:%M:%S")
        return formatter.format(record)


logger = None


def get_logger():
    global logger
    if logger is None:
        # Retrieve LOGLEVEL from environment or set default to 'INFO'
        log_level = os.getenv("LOGLEVEL", "INFO").upper()

        # Important: async logging.
        # K8s redirects stderr/stdout to a file so writes to it may block if disk i/o is
        # slow. It may occur when other pods on the same node are downloading huge
        # models. Hence we do logging only on a separate thread.
        logger = logging.getLogger()
        logger.setLevel(log_level)  # Set the log level

        # Remove all previously configured handlers to enforce async logging.
        # If additional handlers are needed, please add them after import this module.
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        log_queue = queue.Queue()
        queue_handler = logging.handlers.QueueHandler(log_queue)
        logger.addHandler(queue_handler)

        # Force all logs at level < ERROR to go to stdout, and all logs at level >= ERROR to go to stderr
        # This makes it so that unstructured log parsing by google cloud logging (formerly StackDriver)
        # doesn't spuriously count random log lines as errors
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(ColoredFormatter())
        stdout_handler.setLevel(logging.INFO)

        # Handler for WARNING and above -> stderr so GCP treats them as ERROR
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(ColoredFormatter())
        stderr_handler.setLevel(logging.WARNING)

        # Add handlers to the logger
        queue_listener = logging.handlers.QueueListener(
            log_queue, stdout_handler, stderr_handler, respect_handler_level=True
        )
        queue_listener.start()
        atexit.register(queue_listener.stop)
        # Redirect uvicorn logs to the same queue
        UVICORN_LOGGING_CONFIG = copy.deepcopy(uvicorn.config.LOGGING_CONFIG)
        for _, handler_conf in UVICORN_LOGGING_CONFIG["handlers"].items():
            handler_conf["class"] = "logging.handlers.QueueHandler"
            handler_conf["queue"] = log_queue
            del handler_conf["stream"]

    return logger
