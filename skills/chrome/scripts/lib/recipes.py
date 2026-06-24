"""High-level search, fetch, and audit recipes."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from .cdp import (
    close_browser_session,
    emulate_page,
    launch_browser,
    navigate_page,
    screenshot_page,
    wait_page,
)
from .extract_a11y import extract_a11y
from .extract_article import extract_article
from .extract_search import extract_serp
from .layout_probe import DEFAULT_RULES, extract_layout

DEFAULT_VIEWPORT_HEIGHTS: dict[int, int] = {
    375: 667,
    390: 844,
    768: 1024,
    1024: 768,
    1280: 720,
    1440: 900,
    1920: 1080,
}


def parse_viewports(spec: str) -> list[tuple[int, int]]:
    viewports: list[tuple[int, int]] = []
    for part in spec.split(","):
        item = part.strip().lower()
        if not item:
            continue
        if "x" in item:
            width_s, height_s = item.split("x", 1)
            viewports.append((int(width_s), int(height_s)))
        else:
            width = int(item)
            height = DEFAULT_VIEWPORT_HEIGHTS.get(width, int(width * 1.78))
            viewports.append((width, height))
    if not viewports:
        viewports = [(1280, 720)]
    return viewports


def _parse_csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


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


async def audit_url(
    url: str,
    *,
    viewports: str = "375,1280",
    selectors: str | None = None,
    rules: str | None = None,
    include_screenshot: bool = False,
    include_a11y: bool = False,
    timeout_ms: int = 25000,
    headed: bool = False,
    user_data_dir: str | None = None,
    wait_selector: str | None = None,
) -> dict[str, Any]:
    parsed_viewports = parse_viewports(viewports)
    selector_list = _parse_csv(selectors, [])
    rule_list = _parse_csv(rules, DEFAULT_RULES)
    first_w, first_h = parsed_viewports[0]

    launch = await launch_browser(
        headed=headed,
        user_data_dir=user_data_dir,
        viewport=(first_w, first_h),
    )
    session_id = launch["session_id"]
    screenshot_dir = Path(tempfile.mkdtemp(prefix="chrome-skill-audit-"))

    try:
        await navigate_page(
            session_id,
            url,
            wait="networkidle",
            timeout_ms=timeout_ms,
        )
        if wait_selector:
            await wait_page(session_id, selector=wait_selector, timeout_ms=timeout_ms)

        viewport_results: list[dict[str, Any]] = []
        all_issues: list[dict[str, Any]] = []

        for width, height in parsed_viewports:
            await emulate_page(session_id, width, height)
            await wait_page(session_id, load=True, timeout_ms=5000)

            layout = await extract_layout(
                session_id,
                selectors=selector_list or None,
                rules=rule_list,
            )
            entry: dict[str, Any] = {
                "viewport": {"width": width, "height": height},
                "layout": layout,
                "issues": layout.get("issues", []),
            }

            for issue in layout.get("issues", []):
                tagged = dict(issue)
                tagged["viewport"] = f"{width}x{height}"
                all_issues.append(tagged)

            if include_screenshot:
                shot_path = str(screenshot_dir / f"viewport-{width}x{height}.png")
                shot = await screenshot_page(session_id, path=shot_path)
                entry["screenshot"] = shot.get("path")

            if include_a11y and (width, height) == parsed_viewports[-1]:
                a11y = await extract_a11y(session_id)
                entry["a11y"] = a11y
                for issue in a11y.get("issues", []):
                    tagged = dict(issue)
                    tagged["viewport"] = f"{width}x{height}"
                    all_issues.append(tagged)

            viewport_results.append(entry)

        error_issues = [i for i in all_issues if i.get("severity") == "error"]
        warn_issues = [i for i in all_issues if i.get("severity") == "warn"]

        return {
            "command": "audit",
            "url": url,
            "viewports": [f"{w}x{h}" for w, h in parsed_viewports],
            "viewport_results": viewport_results,
            "issues": all_issues,
            "issue_count": len(all_issues),
            "error_count": len(error_issues),
            "warn_count": len(warn_issues),
            "passed": len(error_issues) == 0,
            "error": None,
        }
    except Exception as exc:
        return {
            "command": "audit",
            "url": url,
            "issues": [],
            "issue_count": 0,
            "passed": False,
            "error": {"code": "audit", "message": str(exc)},
        }
    finally:
        close_browser_session(session_id)
