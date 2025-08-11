import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol, TypeAlias



class MessageType(enum.Enum):
    TELEGRAM = enum.auto()
    MATTERMOST = enum.auto()
    SLACK = enum.auto()


JSON: TypeAlias = dict[str, Any]


@dataclass
class JsonMessage:
    """Сырое сообщение из внешнего источника"""
    message_type: MessageType
    payload: JSON


@dataclass
class ParsedMessage:
    """Унифицированное сообщение системы"""
    source: MessageType
    message_id: str
    chat_id: str | None
    user_id: str | None
    text: str | None
    timestamp: datetime
    attachments: list[Any] = field(default_factory=list)


class Parser(Protocol):
    """Интерфейс парсера конкретного источника"""
    def parse(self, message: JsonMessage) -> ParsedMessage: ...


class TelegramParser:
    """Парсер Telegram"""
    def parse(self, message: JsonMessage) -> ParsedMessage:
        p = message.payload
        msg_id = str(p.get("message_id") or p.get("id") or "")
        text = p.get("text") or p.get("caption")
        user_id = p.get("from", {}).get("id")
        chat_id = p.get("chat", {}).get("id")
        date = p.get("date")
        if date is None:
            raise ValueError("Missing date in telegram payload")
        ts = datetime.fromtimestamp(int(date), tz=timezone.utc)
        return ParsedMessage(
            source=MessageType.TELEGRAM,
            message_id=str(msg_id),
            chat_id=str(chat_id) if chat_id is not None else None,
            user_id=str(user_id) if user_id is not None else None,
            text=text,
            timestamp=ts,
        )


class SlackParser:
    """Парсер Slack"""
    def parse(self, message: JsonMessage) -> ParsedMessage:
        p = message.payload
        text = p.get("text")
        user_id = p.get("user")
        chat_id = p.get("channel")
        ts_raw = p.get("ts")
        if ts_raw is None:
            raise ValueError("Missing ts in slack payload")
        ts_float = float(ts_raw)
        ts = datetime.fromtimestamp(ts_float, tz=timezone.utc)
        msg_id = p.get("client_msg_id") or str(ts_raw)
        return ParsedMessage(
            source=MessageType.SLACK,
            message_id=str(msg_id),
            chat_id=str(chat_id) if chat_id is not None else None,
            user_id=str(user_id) if user_id is not None else None,
            text=text,
            timestamp=ts,
        )


class MattermostParser:
    """Парсер Mattermost"""
    def parse(self, message: JsonMessage) -> ParsedMessage:
        p = message.payload
        text = p.get("message")
        user_id = p.get("user_id")
        chat_id = p.get("channel_id")
        msg_id = p.get("id") or ""
        created = p.get("create_at")
        if created is None:
            raise ValueError("Missing create_at in mattermost payload")
        ts = datetime.fromtimestamp(int(created) / 1000.0, tz=timezone.utc)
        return ParsedMessage(
            source=MessageType.MATTERMOST,
            message_id=str(msg_id),
            chat_id=str(chat_id) if chat_id is not None else None,
            user_id=str(user_id) if user_id is not None else None,
            text=text,
            timestamp=ts,
        )


class ParserFactory:
    """Фабрика парсеров сообщений"""
    _registry: dict[MessageType, Parser] = {
        MessageType.TELEGRAM: TelegramParser(),
        MessageType.SLACK: SlackParser(),
        MessageType.MATTERMOST: MattermostParser(),
    }

    @classmethod
    def get(cls, message_type: MessageType) -> Parser:
        parser = cls._registry.get(message_type)
        if parser is None:
            raise ValueError("Unsupported message type")
        return parser

    @classmethod
    def parse(cls, message: JsonMessage) -> ParsedMessage:
        return cls.get(message.message_type).parse(message)



def main():
    tg = JsonMessage(
        message_type=MessageType.TELEGRAM,
        payload={"message_id": 1, "date": 1731000000, "chat": {"id": -100}, "from": {"id": 42}, "text": "Привет"},
    )
    sl = JsonMessage(
        message_type=MessageType.SLACK,
        payload={"ts": "1254182562.125", "channel": "C1", "user": "U1", "text": "My dog. It looks like a H"},
    )
    mm = JsonMessage(
        message_type=MessageType.MATTERMOST,
        payload={"id": "m1", "create_at": 1754870215123, "channel_id": "CH1", "user_id": "USR", "message": "It's not... I'm not a cat."},
    )

    for raw in (tg, sl, mm):
        parsed = ParserFactory.parse(raw)
        print(f"╭{parsed.source.name} [{parsed.message_id}]\n│{parsed.user_id} -> {parsed.chat_id}: {parsed.text}\n╰{parsed.timestamp.isoformat()}")


if __name__ == "__main__":
    main()
