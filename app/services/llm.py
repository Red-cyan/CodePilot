from dataclasses import dataclass
from typing import Protocol

import httpx

from app.core.config import settings


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str


class LLMClient(Protocol):
    def complete(self, messages: list[ChatMessage], temperature: float = 0.2) -> str:
        raise NotImplementedError


class FallbackLLMClient:
    def complete(self, messages: list[ChatMessage], temperature: float = 0.2) -> str:
        del temperature
        user_message = next(
            (message.content for message in reversed(messages) if message.role == "user"),
            "",
        )
        return (
            "当前未启用真实模型调用，以下是基于检索上下文的本地回退回答。\n\n"
            f"{user_message[:1200]}"
        )


class DeepSeekChatClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or settings.deepseek_api_key
        self._base_url = (base_url or settings.deepseek_base_url).rstrip("/")
        self._model = model or settings.deepseek_model
        self._timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    def complete(self, messages: list[ChatMessage], temperature: float = 0.2) -> str:
        if not self.enabled:
            return FallbackLLMClient().complete(messages, temperature)

        payload = {
            "model": self._model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            return (
                "真实模型调用失败，已切换到本地回退回答。\n\n"
                f"错误信息：{exc}"
            )

        try:
            return str(data["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError):
            return "真实模型返回格式异常，无法提取回答内容。"


def default_llm_client() -> LLMClient:
    return DeepSeekChatClient()
