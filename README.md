# Chat Analytics App

This project contains a Steamship App to analyse and structure chat room message:

* Cluster chat messages into single topic conversations.
* Classify the sentiment of a chat message.
* Classify the intent of a chat message.

## Configuration

This plugin must be configured with the following fields:

| Parameter | Description | DType | Required |
|-------------------|----------------------------------------------------|--------|--|
| oneai_api_key | Your bearer token to access the One AI API | string | Yes |
| hf_api_bearer_token | Your bearer token to access the Hugging Face API | string | Yes |
| hf_model_path | The model path of the HF model you want to use for intent classification. | string | No |

## Usage

```python
from steamship import App, AppInstance, Steamship
from typing import List
from src.api_spec import Message

APP_HANDLE = 'chat-analytics-app'
PLUGIN_CONFIG = {
    "oneai_api_key": "FILL_IN",
    "hf_api_bearer_token": "FILL_IN",
    "hf_model_path": "FILL_IN",
}
steamship = Steamship(profile="staging")  # Without arguments, credentials in ~/.steamship.json will be used.
# Fetch app definition
app = App.get(steamship, handle=APP_HANDLE).data
# Instantiate app
app_instance = AppInstance.create(
    steamship,
    app_id=app.id,
    config=PLUGIN_CONFIG,
).data
# Analyze a stream of chat messages
chat_stream: List[Message] = []
app_instance.post("analyze", chat_stream=chat_stream)
```

## Developing

Development instructions are located in [DEVELOPING.md](DEVELOPING.md)

## Testing

Testing instructions are located in [TESTING.md](TESTING.md)

## Deploying

Deployment instructions are located in [DEPLOYING.md](DEPLOYING.md)
