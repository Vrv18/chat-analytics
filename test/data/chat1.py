"""Example of a unthreaded chat conversation."""
from datetime import datetime

from api_spec import Intent, Message

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
