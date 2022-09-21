"""Test zendesk-ticket-urgency via unit tests."""
from copy import deepcopy
from typing import List

import pytest
from steamship import Steamship

from api_spec import Message
from src.api import ChatAnalyticsApp
from tests.utils import CONVERSATIONS, validate_response, delete_files_in_space, check_if_space_is_empty, \
    check_successful_storage

ENVIRONMENT = "abbot"


@pytest.mark.parametrize("chat_stream", CONVERSATIONS)
def test_analyze(chat_stream: List[Message]) -> None:
    """Test analyze endpoint."""
    client = Steamship(profile=ENVIRONMENT)

    app = ChatAnalyticsApp(client)

    response = app.analyze(
        chat_stream=[message.dict(format_dates=True, format_enums=True) for message in chat_stream]
    )

    validate_response(chat_stream, response)


@pytest.mark.parametrize("chat_stream", CONVERSATIONS)
def test_analyze_threading_logic(chat_stream: List[Message]) -> None:
    """Test analyze endpoint."""
    client = Steamship(profile=ENVIRONMENT)
    app = ChatAnalyticsApp(client)

    chat_stream_0 = deepcopy(chat_stream)

    chat_stream_0[0].root_message_id = "1"

    message_input = [
        message.dict(format_dates=True, format_enums=True) for message in chat_stream_0
    ]
    import json
    print(json.dumps(message_input))

    response = app.analyze(
        chat_stream=[
            message.dict(format_dates=True, format_enums=True) for message in chat_stream_0
        ]
    )

    validate_response(chat_stream_0, response)

    chat_stream_1 = deepcopy(chat_stream)

    chat_stream_1[0].root_message_id = "0"
    chat_stream_1[1].root_message_id = "0"
    chat_stream_1[2].root_message_id = "0"

    response = app.analyze(
        chat_stream=[
            message.dict(format_dates=True, format_enums=True) for message in chat_stream_1
        ]
    )

    validate_response(chat_stream_1, response)

    chat_stream_2 = deepcopy(chat_stream)

    chat_stream_2[0].message_id = "-1"
    chat_stream_2[0].root_message_id = "-1"
    chat_stream_2[0].message_id = "-2"
    chat_stream_2[0].root_message_id = "-2"

    response = app.analyze(
        chat_stream=[
            message.dict(format_dates=True, format_enums=True) for message in chat_stream_2
        ]
    )

    validate_response(chat_stream_2, response)


@pytest.mark.parametrize("chat_stream", CONVERSATIONS)
def test_add_examples(chat_stream: List[Message]) -> None:
    client = Steamship(profile=ENVIRONMENT)
    app = ChatAnalyticsApp(client)

    # First we delete all the files in the space
    delete_files_in_space(client)

    # Then we check if it is really empty
    check_if_space_is_empty(client)

    app.add_examples(
        chat_stream=[
            message.dict(format_dates=True, format_enums=True) for message in chat_stream
        ]
    )

    check_successful_storage(chat_stream, client)
