"""High-level search and fetch recipes."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from .cdp import (
    close_browser_session,
    launch_browser,
    navigate_page,
    wait_page,
)
from .extract_article import extract_article
from .extract_search import extract_serp


async def fetch_url(
    url: str,
    *,
    timeout_ms: int = 25000,
    headed: bool = False,
    user_data_dir: str | None = None,
) -> dict[str, Any]:
    launch = await launch_browser(headed=headed, user_data_dir=user_data_dir)
    session_id = launch["session_id"]
    try:
        await navigate_page(
            session_id,
            url,
            wait="networkidle",
            timeout_ms=timeout_ms,
        )
        article = await extract_article(session_id)
        return {
            "command": "fetch",
            "url": url,
            "final_url": article.get("final_url", url),
            "title": article.get("title"),
            "description": article.get("description"),
            "content_markdown": article.get("content_markdown", ""),
            "headings": article.get("headings", []),
            "word_count": article.get("word_count", 0),
            "fetched_at": article.get("fetched_at"),
            "error": article.get("error"),
        }
    except Exception as exc:
        return {
            "command": "fetch",
            "url": url,
            "error": {"code": "fetch", "message": str(exc)},
        }
    finally:
        close_browser_session(session_id)


async def search_google(
    query: str,
    *,
    limit: int = 10,
    lang: str = "en",
    timeout_ms: int = 25000,
    headed: bool = False,
    user_data_dir: str | None = None,
) -> dict[str, Any]:
    launch = await launch_browser(headed=headed, user_data_dir=user_data_dir)
    session_id = launch["session_id"]
    search_url = (
        f"https://www.google.com/search?q={quote_plus(query)}&hl={quote_plus(lang)}"
    )
    try:
        await navigate_page(session_id, search_url, wait="load", timeout_ms=timeout_ms)
        await wait_page(session_id, networkidle=True, timeout_ms=timeout_ms)
        serp = await extract_serp(session_id, limit=limit)
        return {
            "command": "search",
            "query": query,
            "engine": "google",
            "results": serp.get("results", []),
            "result_count": serp.get("result_count", 0),
            "error": serp.get("error"),
        }
    except Exception as exc:
        return {
            "command": "search",
            "query": query,
            "engine": "google",
            "results": [],
            "result_count": 0,
            "error": {"code": "search", "message": str(exc)},
        }
    finally:
        close_browser_session(session_id)
