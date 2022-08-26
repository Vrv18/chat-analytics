"""Integration tests for the chat-analytics-app."""
from typing import List

import pytest
from steamship import App, AppInstance, Steamship

from api_spec import Message
from tests.utils import CONVERSATIONS, load_config, validate_response, delete_files_in_space, check_if_space_is_empty, \
    check_successful_storage

ENVIRONMENT = "abbot"
APP_HANDLE = "chat-analytics-app"


def _get_app_instance():
    client = Steamship(profile=ENVIRONMENT)
    config = load_config()

    app = App.get(client, handle=APP_HANDLE).data
    assert app is not None
    assert app.id is not None

    app_instance = AppInstance.create(client, app_id=app.id, config=config).data
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
