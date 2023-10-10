from typing import AsyncIterable

from fastapi_poe import PoeBot
from fastapi_poe.client import MetaMessage, stream_request
from fastapi_poe.types import (
    QueryRequest,
    SettingsRequest,
    SettingsResponse,
)

from sse_starlette.sse import ServerSentEvent

from corpus import retrieve_related_sentences, load_corpus
from prompt import get_prompt

BOT = "ChatGPT"
NUM_RELATED_SENTENCES = 20
FULL_CORPUS = load_corpus()


class AkkadianTalkerBot(PoeBot):

    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        # Get user's latest query for which we want to do RAG by retrieving relevant sentences
        user_question = query.query[-1].content

        # Get the most relevant sentences for this query from the full corpus
        related_corpus = retrieve_related_sentences(FULL_CORPUS, user_question, top_n=NUM_RELATED_SENTENCES)

        # Append the user's latest query with the standard prompt and related corpus
        query.query[-1].content = get_prompt(user_question, "\n".join(related_corpus), BOT)

        # Send the query to BOT and get the response
        async for msg in stream_request(request=query, bot_name=BOT, access_key=query.access_key):
            if isinstance(msg, MetaMessage):
                continue
            elif msg.is_suggested_reply:
                yield self.suggested_reply_event(msg.text)
            elif msg.is_replace_response:
                yield self.replace_response_event(msg.text)
            else:
                yield self.text_event(msg.text)

    async def get_settings(self, settings: SettingsRequest) -> SettingsResponse:
        return SettingsResponse(
            server_bot_dependencies={BOT: 1},
        )
