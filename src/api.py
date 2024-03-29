"""App that summarizes meetings using Amazon Transcribe and OneAI skills."""
from collections import Counter
from itertools import zip_longest
from typing import Any, Dict, List, Type

from pydantic import parse_obj_as
from steamship import Block, File, Steamship, Tag
from steamship.invocable import Config, InvocableResponse, PackageService, create_handler, post

from api_spec import Intent, Message, Sentiment

PRIORITY_LABEL: str = "priority"
HF_MODEL_PATH: str = "typeform/distilbert-base-uncased-mnli"


class ChatAnalyticsPackage(PackageService):
    """App that transcribes and summarizes audio using Amazon Transcribe and OneAI skills."""

    def config_cls(self) -> Type[Config]:
        """Config used to initialize a ChatAnalyticsPackage."""
        return Config

    ONEAI_TAGGER_HANDLE = "oneai-tagger"
    ZERO_SHOT_TAGGER_HANDLE = "zero-shot-tagger-default"

    def __init__(self, client: Steamship = None, config: Dict[str, Any] = None):
        super().__init__(client, config)

        self.oneai_tagger = client.use_plugin(
            plugin_handle=self.ONEAI_TAGGER_HANDLE,
            instance_handle=self.ONEAI_TAGGER_HANDLE + "1",
            config={
                "skills": ",".join(["dialogue-segmentation", "sentiments"]),
            },
        )

        self.intent_tagger = client.use_plugin(
            plugin_handle=self.ZERO_SHOT_TAGGER_HANDLE,
            instance_handle=self.ZERO_SHOT_TAGGER_HANDLE + "1",
            config={
                "hf_model_path": HF_MODEL_PATH,
                "labels": "hello,praise,complaint,question,request,explanation",
                "tag_kind": "intent",
                "multi_label": False,
                "use_gpu": False,
            },
        )

    @post("analyze")
    def analyze(self, chat_stream: List[Dict[str, Any]]) -> InvocableResponse[List[Message]]:
        """Analyze a stream of chat messages and add useful features."""
        chat_stream = self._parse_input(chat_stream)

        tags, text = [], []
        i = 0
        for message in chat_stream:
            text.append(message.text)
            message_length = len(message.text)
            tags.append(
                Tag(
                    kind="speaker",
                    start_idx=i,
                    end_idx=i + message_length,
                    name=message.user_id,
                )
            )
            i += message_length

        single_block_file = File(
            blocks=[
                Block(
                    text="".join(text),
                    tags=tags,
                )
            ],
        )

        multi_block_file = File(
            blocks=[
                Block.CreateRequest(
                    text=message.text,
                )
                for message in chat_stream
            ],
        )

        tag_result_oneai_task = self.oneai_tagger.tag(doc=single_block_file)
        tag_result_intent_task = self.intent_tagger.tag(doc=multi_block_file)

        tag_result_oneai_task.wait()
        single_block_file = tag_result_oneai_task.output.file

        tag_result_intent_task.wait()
        multi_block_file = tag_result_intent_task.output.file

        thread_tags = sorted(
            [
                tag
                for tag in single_block_file.blocks[0].tags
                if tag.kind == "dialogue-segmentation"
            ],
            key=lambda x: x.start_idx,
        )
        sentiment_tags = sorted(
            [tag for tag in single_block_file.blocks[0].tags if tag.kind == "sentiments"],
            key=lambda x: x.start_idx,
        )
        i = 0
        thread_idx = 0
        root_message_id = None
        for message, message_block in zip_longest(chat_stream, multi_block_file.blocks):
            if i > thread_tags[thread_idx].end_idx:
                thread_idx += 1
                root_message_id = (
                    message.message_id
                    if message.root_message_id is None
                    else message.root_message_id
                )
            if message.root_message_id is None:
                message.root_message_id = root_message_id or message.message_id
            else:
                root_message_id = message.root_message_id

            if message.intent is None:
                intent_tags = [tag for tag in message_block.tags if tag.kind == "intent"]
                if intent_tags:
                    intent_tag = intent_tags[0]
                    intent_tag.name = (
                        "salutation" if intent_tag.name == "hello" else intent_tag.name
                    )
                    message.intent = Intent(intent_tag.name.title())

            if message.sentiment is None:
                local_sentiment_tags = [
                    sentiment_tag
                    for sentiment_tag in sentiment_tags
                    if sentiment_tag.start_idx - len(message.text) <= i <= sentiment_tag.end_idx
                ]
                if local_sentiment_tags:
                    sentiment_tag = Counter(
                        sentiment_tag.name for sentiment_tag in local_sentiment_tags
                    ).most_common(1)[0][0]
                    message.sentiment = (
                        Sentiment.POSITIVE if sentiment_tag == "POS" else Sentiment.NEGATIVE
                    )
                else:
                    message.sentiment = Sentiment.NEUTRAL

            i += len(message.text) + 1

        return InvocableResponse(
            json={
                "chat_stream": [
                    message.dict(format_dates=True, format_enums=True) for message in chat_stream
                ]
            }
        )

    def _parse_input(self, chat_stream):
        if isinstance(chat_stream, list) and not isinstance(chat_stream[0], Message):
            chat_stream = parse_obj_as(List[Message], chat_stream)
        return chat_stream

    @post("add_examples")
    def add_examples(self, chat_stream: List[Message]) -> InvocableResponse:
        """Add examples for the AI to train on."""
        chat_stream = self._parse_input(chat_stream)

        File.create(
            self.client,
            blocks=[
                Block.CreateRequest(text=message.text, tags=message.extract_tags())
                for message in chat_stream
            ],
        )
        return InvocableResponse(string="Successfully uploaded examples.")


handler = create_handler(ChatAnalyticsPackage)
