"""Api specification for the chat analytics app."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from steamship import Tag


class Intent(str, Enum):
    """Intent of a chat message."""

    SALUTATION = "Salutation"
    PRAISE = "Praise"
    COMPLAINT = "Complaint"
    QUESTION = "Question"
    REQUEST = "Request"
    EXPLANATION = "Explanation"


class Sentiment(str, Enum):
    """Sentiment of a chat message."""

    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"


class Message(BaseModel):
    """Structured representation of a chat message."""

    message_id: str = Field(example="001")
    timestamp: datetime
    user_id: str = Field(example="u001")
    text: str = Field(example="Hello. This is a message.")
    sentiment: Optional[Sentiment]
    intent: Optional[Intent]
    root_message_id: Optional[str] = Field(example="001")

    def dict(self, format_dates: bool = False, format_enums: bool = False, **kwargs):
        """Transform object into a dictionary."""
        output = super().dict(**kwargs)
        for k, v in output.items():
            if format_dates and isinstance(v, datetime):
                output[k] = v.isoformat()
            if format_enums and isinstance(v, Enum):
                output[k] = v.value
        return output

    def extract_tags(self):
        """Extract from OneAI's API response."""
        return [
            Tag.CreateRequest(
                kind="sentiments", name=self.sentiment.value if self.sentiment else ""
            ),
            Tag.CreateRequest(kind="intent", name=self.intent.value if self.intent else ""),
            Tag.CreateRequest(kind="root_message_id", name=str(self.root_message_id or "")),
            Tag.CreateRequest(kind="timestamp", name=str(self.timestamp) if self.timestamp else ""),
            Tag.CreateRequest(kind="user_id", name=str(self.user_id or "")),
            Tag.CreateRequest(kind="message_id", name=str(self.message_id or "")),
        ]
