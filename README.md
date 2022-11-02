# Chat Analytics App

This project contains a Steamship App to analyse and structure chat room message:

* Cluster chat messages into single topic conversations.
* Classify the sentiment of a chat message.
* Classify the intent of a chat message.

## Usage

```python
from steamship import Steamship
from typing import List
from src.api_spec import Message

PACKAGE_HANDLE = 'chat-analytics-app'
ship = Steamship(profile="staging")  # Without arguments, credentials in ~/.steamship.json will be used.
# Fetch app definition
package_instance = ship.use(package_handle=PACKAGE_HANDLE, instance_handle=PACKAGE_HANDLE)
chat_stream: List[Message] = [Message()]
package_instance.invoke("analyze", chat_stream=chat_stream)
```

## Developing

Development instructions are located in [DEVELOPING.md](DEVELOPING.md)

## Testing

Testing instructions are located in [TESTING.md](TESTING.md)

## Deploying

Deployment instructions are located in [DEPLOYING.md](DEPLOYING.md)
