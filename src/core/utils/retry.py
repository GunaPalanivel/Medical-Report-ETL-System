import time
from functools import wraps
from typing import Callable, TypeVar


F = TypeVar("F", bound=Callable[..., object])


def retry_on_exception(max_attempts: int = 3, backoff_multiplier: int = 2):
    """Retry decorator with exponential backoff."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = 1
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts:
                        raise
                    time.sleep(delay)
                    delay *= backoff_multiplier

        return wrapper  # type: ignore[return-value]

    return decorator
