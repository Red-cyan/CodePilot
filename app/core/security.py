from secrets import compare_digest

from fastapi import Header, HTTPException

from app.core.config import settings


def require_api_key(x_codepilot_api_key: str | None = Header(default=None)) -> None:
    if not settings.api_key:
        return
    if x_codepilot_api_key and compare_digest(x_codepilot_api_key, settings.api_key):
        return
    raise HTTPException(status_code=401, detail="缺少或无效的 CodePilot API Key")
