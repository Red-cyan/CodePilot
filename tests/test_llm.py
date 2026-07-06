import httpx

from app.services.llm import ChatMessage, DeepSeekChatClient


def test_deepseek_client_falls_back_without_api_key():
    client = DeepSeekChatClient(api_key="", base_url="https://example.com", model="test")

    answer = client.complete([ChatMessage(role="user", content="解释仓库导入逻辑")])

    assert "本地回退回答" in answer


def test_deepseek_client_parses_openai_compatible_response(monkeypatch):
    def fake_post(self, url, json, headers):  # noqa: ANN001
        del self, url, json, headers
        return httpx.Response(
            status_code=200,
            request=httpx.Request("POST", "https://example.com/chat/completions"),
            json={"choices": [{"message": {"content": "模型回答"}}]},
        )

    monkeypatch.setattr(httpx.Client, "post", fake_post)
    client = DeepSeekChatClient(api_key="key", base_url="https://example.com", model="test")

    answer = client.complete([ChatMessage(role="user", content="hello")])

    assert answer == "模型回答"
