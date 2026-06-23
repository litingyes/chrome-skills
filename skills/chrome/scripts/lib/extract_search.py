"""Google SERP extraction from the current page."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from .cdp import _with_page_session

SERP_JS = r"""
(limit => {
  const bodyText = document.body ? document.body.innerText : '';
  const hasCaptcha = Boolean(
    document.querySelector('.g-recaptcha, #captcha, form#captcha-form') ||
    /unusual traffic|not a robot|verify you are human/i.test(bodyText)
  );
  if (hasCaptcha) {
    return {
      blocked: true,
      results: [],
      result_count: 0,
    };
  }

  const cleanUrl = (href) => {
    if (!href) return null;
    try {
      const url = new URL(href, window.location.href);
      if (url.hostname.endsWith('google.com') && url.pathname === '/url') {
        const target = url.searchParams.get('q') || url.searchParams.get('url');
        if (target) return target;
      }
      return url.href;
    } catch {
      return null;
    }
  };

  const isExternal = (href) => {
    if (!href) return false;
    try {
      const host = new URL(href, window.location.href).hostname;
      return !host.endsWith('google.com');
    } catch {
      return false;
    }
  };

  const seen = new Set();
  const results = [];

  const pushResult = (title, url, snippet) => {
    if (!title || !url || !isExternal(url)) return;
    if (seen.has(url)) return;
    seen.add(url);
    results.push({
      rank: results.length + 1,
      title: title.trim(),
      url,
      snippet: (snippet || '').trim(),
    });
  };

  const containers = document.querySelectorAll('div.g, div[data-sokoban-container] div.MjjYud, div#search div[data-hveid]');
  for (const container of containers) {
    const heading = container.querySelector('h3');
    const link = heading ? heading.closest('a[href]') : container.querySelector('a[href]');
    if (!link) continue;
    const title = heading ? heading.innerText : link.innerText;
    const url = cleanUrl(link.href);
    const snippetNode = container.querySelector('.VwiC3b, .IsZvec, .st, span[data-sncf]');
    const snippet = snippetNode ? snippetNode.innerText : '';
    pushResult(title, url, snippet);
    if (results.length >= limit) break;
  }

  if (!results.length) {
    for (const heading of document.querySelectorAll('a h3')) {
      const link = heading.closest('a');
      if (!link) continue;
      const title = heading.innerText;
      const url = cleanUrl(link.href);
      const container = link.closest('div');
      const snippet = container
        ? (container.innerText || '').replace(title, '').trim()
        : '';
      pushResult(title, url, snippet);
      if (results.length >= limit) break;
    }
  }

  return {
    blocked: false,
    results,
    result_count: results.length,
  };
})
"""


async def extract_serp(session_id: str, *, limit: int = 10) -> dict[str, Any]:
    client, _ = await _with_page_session(session_id)
    try:
        data = await client.evaluate(f"({SERP_JS})({int(limit)})", await_promise=False)
        if not isinstance(data, dict):
            raise RuntimeError("SERP extraction returned unexpected payload")

        payload: dict[str, Any] = {
            "command": "extract",
            "mode": "serp",
            "engine": "google",
            "results": data.get("results", []),
            "result_count": data.get("result_count", 0),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "error": None,
        }

        if data.get("blocked"):
            payload["results"] = []
            payload["result_count"] = 0
            payload["error"] = {
                "code": "captcha",
                "message": "Google returned a CAPTCHA or bot-check page.",
                "remediation": (
                    "Retry with headed mode and a real profile: "
                    "cdp launch --headed --user-data-dir <path>, then navigate and extract serp."
                ),
            }
        elif payload["result_count"] == 0:
            host = ""
            url = await client.current_url()
            try:
                host = urlparse(url).hostname or ""
            except Exception:
                pass
            if "google." in host:
                payload["error"] = {
                    "code": "parse",
                    "message": "No Google search results could be parsed from the current page.",
                    "remediation": "Confirm the page is a Google SERP or retry with --headed.",
                }

        return payload
    finally:
        await client.close()
