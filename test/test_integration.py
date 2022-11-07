"""Integration test for the chat-analytics-app."""
import random
import string

from test.utils import (
    CONVERSATIONS,
    check_if_space_is_empty,
    check_successful_storage,
    delete_files_in_space,
    validate_response,
)
from typing import List

import pytest
from steamship import Steamship

from api_spec import Message

ENVIRONMENT = "prod"
APP_HANDLE = "chat-analytics"


def random_name() -> str:
    """Returns a random name suitable for a handle that has low likelihood of colliding with another.

    Output format matches test_[a-z0-9]+, which should be a valid handle.
    """
    letters = string.digits + string.ascii_letters
    return f"test_{''.join(random.choice(letters) for _ in range(10))}".lower()  # noqa: S311


def _get_app_instance(): 
    client = Steamship(profile=ENVIRONMENT)

    app_instance = client.use(package_handle=APP_HANDLE, instance_handle=random_name(), fetch_if_exists=False)
    assert app_instance is not None
    assert app_instance.id is not None

    return app_instance


@pytest.mark.parametrize("chat_stream", CONVERSATIONS)
def test_analyze(chat_stream: List[Message]) -> None:
    """Test analyze endpoint."""
    app_instance = _get_app_instance()

    response = app_instance.invoke(
        "analyze",
        chat_stream=[message.dict(format_dates=True, format_enums=True) for message in chat_stream],
    )

    validate_response(chat_stream, response)


@pytest.mark.parametrize("chat_stream", CONVERSATIONS)
def test_add_examples(chat_stream: List[Message]) -> None:
    """Test add_examples endpoint."""
    client = Steamship(profile=ENVIRONMENT)
    app_instance = _get_app_instance()

    # First we delete all the files in the space
    delete_files_in_space(client)

    # Then we check if it is really empty
    check_if_space_is_empty(client)

    app_instance.invoke(
        "add_examples",
        chat_stream=[message.dict(format_dates=True, format_enums=True) for message in chat_stream],
    )

    check_successful_storage(chat_stream, client)
