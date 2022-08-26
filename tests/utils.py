"""Collection of utility function to support testing."""
import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import parse_obj_as
from steamship import File, Steamship
from steamship.app import Response

from api_spec import Intent, Message
from tests import TEST_DATA


def load_config() -> Dict[str, Any]:
    """Load config from test data."""
    return json.load((TEST_DATA / "config.json").open())


CONVERSATIONS = [
    [
        Message(
            message_id="0",
            timestamp=datetime(2022, 6, 15, 16, 18, 33, 100),
            user_id="1",
            text="Hi Team!",
            intent=Intent.SALUTATION,
        ),
        Message(
            message_id="1",
            timestamp=datetime(2022, 6, 15, 16, 18, 33, 960),
            user_id="1",
            text="Thanks for getting back to us on the styling issue "
                 "we had last week. Font colours are so important for productivity.",
            intent=Intent.PRAISE,
        ),
        Message(
            message_id="2",
            timestamp=datetime(2022, 6, 15, 16, 18, 34, 450),
            user_id="1",
            text="I noticed ab.bot being very verbose lately",
        ),
        Message(
            message_id="3",
            timestamp=datetime(2022, 6, 15, 16, 18, 34, 990),
            user_id="1",
            text="Is there a way to decrease the verbosity level?",
        ),
        Message(
            message_id="4",
            timestamp=datetime(2022, 6, 15, 16, 18, 36, 211),
            user_id="1",
            text="I want ab.bot to ignore thank you messages and stop "
                 "asking our customers to assign messages to threads.",
        ),
        Message(
            message_id="5",
            timestamp=datetime(2022, 6, 15, 16, 18, 42, 97),
            user_id="1",
            text="Our clients are not technical so working with threads is difficult.",
        ),
        Message(
            message_id="6",
            timestamp=datetime(2022, 6, 15, 16, 18, 44, 155),
            user_id="1",
            text="Thanks again, looking forward to your response!",
        ),
        Message(
            message_id="7",
            timestamp=datetime(2022, 6, 15, 16, 18, 44, 822),
            user_id="1",
            text="Oh, before I forget. Is there a settings to change the font size?",
        ),
    ]
]


def validate_response(chat_stream: List[Message], response: Response):
    """Validate responses of the chat-analytics-app."""
    processed_chat_stream = parse_obj_as(List[Message], response.data["chat_stream"])
    assert response.data is not None

    last_root_message_id = None
    prediction_start_idx = 0
    for idx, (original_message, processed_message) in enumerate(
            zip(chat_stream, processed_chat_stream)
    ):
        if original_message.intent is None:
            assert processed_message.intent is not None
        else:
            assert processed_message.intent == original_message.intent

        if original_message.sentiment is None:
            assert processed_message.sentiment is not None
        else:
            assert processed_message.sentiment == original_message.sentiment

        if original_message.root_message_id is None:
            assert processed_message.root_message_id is not None
            assert (
                    last_root_message_id is None
                    or processed_message.root_message_id == last_root_message_id
                    or processed_message.root_message_id
                    in {message.message_id for message in chat_stream[prediction_start_idx:]}
            )
        else:
            assert processed_message.root_message_id == original_message.root_message_id
            last_root_message_id = processed_message.root_message_id
            prediction_start_idx = idx + 1


def check_successful_storage(chat_stream, client):
    assert len(File.query(client, "all").data.files) == 1
    assert len(File.query(client, 'blocktag and kind "message_id"').data.files) == 1
    assert len(File.query(client, 'blocktag and kind "user_id"').data.files) == 1
    assert len(File.query(client, 'blocktag and kind "timestamp"').data.files) == 1
    assert len(File.query(client, 'blocktag and kind "sentiments"').data.files) == 1
    assert len(File.query(client, 'blocktag and kind "intent"').data.files) == 1
    assert len(File.query(client, 'blocktag and kind "root_message_id"').data.files) == 1
    file = File.query(client, "all").data.files[0]
    assert len(file.blocks) == len(chat_stream)
    for message, block in zip(chat_stream, file.blocks):

        assert message.text == block.text

        for property in {property for property in message.__dict__.keys() if property not in ("text",)}:
            property_kind = f"{property}s" if property == "sentiment" else property
            property_tags = [tag for tag in block.tags if tag.kind == property_kind]
            assert len(property_tags) == 1
            property_value = getattr(message, property, "") or ""
            if isinstance(property_value, Enum):
                property_value = property_value.value
            property_value = str(property_value)
            assert property_value == property_tags[0].name


def delete_files_in_space(client: Steamship) -> None:
    for file in File.list(client).data.files:
        file.delete()


def check_if_space_is_empty(client):
    assert len(File.query(client, "all").data.files) == 0
