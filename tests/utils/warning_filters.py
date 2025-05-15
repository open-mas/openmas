"""Utility functions for filtering warnings in tests.

This module provides functions to help filter and manage warnings that appear
during test execution. It should be used in test files or test fixtures to
suppress expected warnings.
"""

import contextlib
import warnings
from typing import Generator, List, Optional, Pattern, Type, Union

# Common warning categories that might need to be filtered
# Note: Not all of these are directly available in the warnings module
# so we use strings for filtering
RESOURCE_WARNING = "ResourceWarning"
RUNTIME_WARNING = "RuntimeWarning"
DEPRECATION_WARNING = "DeprecationWarning"
IMPORT_WARNING = "ImportWarning"


def ignore_coroutine_never_awaited() -> None:
    """Filter the common 'coroutine was never awaited' warnings.

    Use this in tests that involve mocking async methods where those
    warnings are expected and unavoidable.
    """
    warnings.filterwarnings("ignore", message="coroutine '.*' was never awaited", category=RuntimeWarning)


def ignore_resource_warnings() -> None:
    """Filter common resource warnings about unclosed sockets and transports.

    Use this in tests involving network clients and servers that might
    not fully close due to test teardown.
    """
    warnings.filterwarnings("ignore", message="unclosed <socket.socket.*", category=ResourceWarning)
    warnings.filterwarnings("ignore", message="unclosed transport.*", category=ResourceWarning)


def ignore_deprecated_event_loop() -> None:
    """Filter deprecation warnings about event loops in asyncio code.

    Use this when testing with libraries that trigger asyncio-related
    deprecation warnings.
    """
    warnings.filterwarnings("ignore", message="The loop argument is deprecated since.*", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message="There is no current event loop.*", category=DeprecationWarning)


@contextlib.contextmanager
def catch_warnings_with_filtering(
    ignore_list: Optional[List[Union[Type[Warning], str, Pattern]]] = None,
) -> Generator[List[warnings.WarningMessage], None, None]:
    """Context manager to catch warnings with custom filtering.

    This extends the standard warnings.catch_warnings context manager by
    allowing you to specify which warning types to ignore.

    Args:
        ignore_list: Optional list of warning types or message patterns to ignore.
            Can include:
            - Warning class types (e.g., RuntimeWarning)
            - Strings that match part of the warning message (e.g., "unclosed")
            - Compiled regex patterns for more precise message matching

    Returns:
        A generator yielding a list of caught warnings that weren't ignored

    Example:
        ```python
        with catch_warnings_with_filtering(["coroutine '.*' was never awaited", "unclosed"]) as w:
            # Run code that might produce warnings
            assert len(w) == 0  # No warnings except the ignored ones
        ```

    Notes:
        - This should be used primarily for testing warning filtering itself
        - For general test code, prefer using the pytest.ini filters
        - Document why specific warnings are being filtered when using this function
    """
    with warnings.catch_warnings(record=True) as recorded_warnings:
        warnings.simplefilter("always")  # Record all warnings

        # Run the code that might produce warnings
        yield recorded_warnings

        # Filter out ignored warnings (modifying recorded_warnings in-place)
        if ignore_list:
            for i in range(len(recorded_warnings) - 1, -1, -1):
                warning = recorded_warnings[i]
                warning_message = str(warning.message)
                warning_category = warning.category.__name__

                # Check if this warning should be ignored
                for ignore_pattern in ignore_list:
                    # If ignore_pattern is a warning class
                    if isinstance(ignore_pattern, type) and issubclass(ignore_pattern, Warning):
                        if issubclass(warning.category, ignore_pattern):
                            recorded_warnings.pop(i)
                            break
                    # If ignore_pattern is a string
                    elif isinstance(ignore_pattern, str):
                        # Check if it's specifying a category
                        if ignore_pattern in (RESOURCE_WARNING, RUNTIME_WARNING, DEPRECATION_WARNING, IMPORT_WARNING):
                            if warning_category == ignore_pattern:
                                recorded_warnings.pop(i)
                                break
                        # Otherwise treat as a message substring
                        elif ignore_pattern in warning_message:
                            recorded_warnings.pop(i)
                            break
                    # If ignore_pattern is a regex pattern
                    elif hasattr(ignore_pattern, "search"):  # Pattern object
                        if ignore_pattern.search(warning_message):
                            recorded_warnings.pop(i)
                            break


def show_test_warnings() -> None:
    """Enable displaying of warnings during test execution.

    This function configures warnings to be displayed during test runs,
    even if they would normally be filtered by pytest.ini. Useful for
    debugging specific test warning issues.
    """
    warnings.simplefilter("always")  # Show all warnings
    # Explicitly reset any existing filters
    warnings.resetwarnings()

    # Log that warnings are now being shown
    print("WARNING: All warnings will be displayed for this test run")
