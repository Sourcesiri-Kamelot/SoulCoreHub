from fireworks.flumina.logger import get_logger

import contextlib
import time


@contextlib.contextmanager
def log_time(name):
    get_logger().info(f"{name}...")
    s = time.time()
    yield
    dur = time.time() - s
    get_logger().info(f"Done: {dur:.3f}s for '{name}'")
