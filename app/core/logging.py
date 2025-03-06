"""
Logging utilities for the application.
"""

from functools import wraps
from typing import Any, Callable, Optional, Sequence
import inspect
import logfire
import time


def trace(
    name: Optional[str] = None,
    tracked_args: Optional[Sequence[str]] = None,
    exclude_args: Optional[Sequence[str]] = None,
) -> Callable:
    """
    A decorator that creates a Logfire span around a function call and tracks specified arguments.
    Also logs the execution time (latency) of the function.

    Args:
        name: Optional custom name for the span. Defaults to function name
        tracked_args: Sequence of argument names to track. If None, tracks all args
        exclude_args: Sequence of argument names to exclude from tracking

    Example:
        @trace(tracked_args=['user_id', 'action'])
        def process_user_action(user_id: str, action: str, sensitive_data: str):
            ...
    """

    def decorator(func: Callable) -> Callable:
        # Get the function's signature for argument inspection
        sig = inspect.signature(func)

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Determine span name
            span_name = name or func.__name__

            # Bind arguments to their parameter names
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Filter arguments to track
            tracked_values = {}
            for arg_name, arg_value in bound_args.arguments.items():
                # Skip if explicitly excluded
                if exclude_args and arg_name in exclude_args:
                    continue
                # Include if explicitly tracked or if tracking all
                if not tracked_args or arg_name in tracked_args:
                    # Convert argument to string representation if needed
                    try:
                        tracked_values[arg_name] = str(arg_value)
                    except Exception:
                        tracked_values[arg_name] = "<unprintable>"

            # Create span with function arguments as attributes
            start_time = time.time()
            span = logfire.span(span_name, attributes=tracked_values)
            try:
                with span:
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    except Exception as e:
                        # Log exception within the span
                        logfire.error(
                            f"Error in {span_name}",
                            exc_info=e,
                            extra={"error_type": type(e).__name__},
                        )
                        raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                logfire.info(
                    "{span_name} completed in {latency}",
                    span_name=span_name,
                    latency=round(latency_ms, 2),
                )

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            span_name = name or func.__name__

            # Bind arguments to their parameter names
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Filter arguments to track
            tracked_values = {}
            for arg_name, arg_value in bound_args.arguments.items():
                if exclude_args and arg_name in exclude_args:
                    continue
                if not tracked_args or arg_name in tracked_args:
                    try:
                        tracked_values[arg_name] = str(arg_value)
                    except Exception:
                        tracked_values[arg_name] = "<unprintable>"

            # Create span with function arguments as attributes
            start_time = time.time()
            span = logfire.span(span_name, attributes=tracked_values)
            try:
                with span:
                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        logfire.error(
                            f"Error in {span_name}",
                            exc_info=e,
                            extra={"error_type": type(e).__name__},
                        )
                        raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                logfire.info(
                    "{span_name} completed in {latency}",
                    span_name=span_name,
                    latency=round(latency_ms, 2),
                )

        # Return appropriate wrapper based on if function is async
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
