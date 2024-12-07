import logging
from sqlalchemy.exc import IntegrityError, DBAPIError
from functools import wraps
from typing import Callable, TypeVar, Awaitable, Any

# Define a generic type for the return value of the async function
R = TypeVar("R")

logger = logging.getLogger(__name__)


def handle_db_errors(func: Callable[..., Awaitable[R]]) -> Callable[..., Awaitable[R]]:
    """Decorator to handle database-specific errors."""
    # Add more exceptions as needed 
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> R:
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Integrity error in {func.__name__}: {e}")
            raise ValueError(
                "Database integrity error. Possible duplicate entry or constraint violation."
            )
        except DBAPIError as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise RuntimeError("Database operation failed. Please try again later.")

    return wrapper
