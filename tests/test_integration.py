"""Integration tests for the chat-analytics-app."""
from typing import List

import pytest
from steamship import App, AppInstance, Steamship

from api_spec import Message
from tests.utils import (
    CONVERSATIONS,
    check_if_space_is_empty,
    check_successful_storage,
    delete_files_in_space,
    load_config,
    validate_response,
)

ENVIRONMENT = "prod"
APP_HANDLE = "chat-analytics-app"


def _get_app_instance():
    client = Steamship(profile=ENVIRONMENT)

    app_instance = AppInstance.create(client, app_handle=APP_HANDLE, handle=APP_HANDLE, upsert=True).data
    assert app_instance is not None
    assert app_instance.id is not None

    return app_instance


@pytest.mark.parametrize("chat_stream", CONVERSATIONS)
def test_analyze(chat_stream: List[Message]) -> None:
    """Test analyze endpoint."""
    app_instance = _get_app_instance()

    response = app_instance.post(
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

    app_instance.post(
        "add_examples",
        chat_stream=[message.dict(format_dates=True, format_enums=True) for message in chat_stream],
    )

    check_successful_storage(chat_stream, client)
