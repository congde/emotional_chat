import pytest
from pydantic import ValidationError

from backend.models import ChatRequest


@pytest.mark.parametrize("message", ["", "   ", "\t\r\n"])
def test_chat_request_rejects_blank_message(message):
    with pytest.raises(ValidationError, match="消息内容不能为空"):
        ChatRequest(message=message)


def test_chat_request_preserves_non_blank_message_whitespace():
    request = ChatRequest(message="  我想聊聊今天的事  ")

    assert request.message == "  我想聊聊今天的事  "
