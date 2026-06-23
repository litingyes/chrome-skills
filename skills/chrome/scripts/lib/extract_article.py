"""Article extraction from the current page."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .cdp import _with_page_session

ARTICLE_JS = r"""
(() => {
  const pickRoot = () => {
    const candidates = [
      document.querySelector('article'),
      document.querySelector('[role="main"]'),
      document.querySelector('main'),
    ].filter(Boolean);
    if (candidates.length) return candidates[0];

    let best = document.body;
    let bestScore = 0;
    for (const node of document.querySelectorAll('div, section')) {
      const text = (node.innerText || '').trim();
      const links = node.querySelectorAll('a').length + 1;
      const score = text.length / links;
      if (score > bestScore && text.length > 120) {
        best = node;
        bestScore = score;
      }
    }
    return best;
  };

  const root = pickRoot();
  const meta = (name) => {
    const el = document.querySelector(`meta[name="${name}"]`);
    return el ? el.getAttribute('content') : null;
  };
  const canonical = document.querySelector('link[rel="canonical"]');

  const blockTags = new Set(['H1','H2','H3','H4','H5','H6','P','LI','BLOCKQUOTE']);
  const lines = [];
  const headings = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
  let node = walker.currentNode;
  while (node) {
    const tag = node.tagName;
    if (blockTags.has(tag)) {
      const text = (node.innerText || '').trim();
      if (!text) {
        node = walker.nextNode();
        continue;
      }
      if (tag.startsWith('H')) {
        const level = Number(tag.slice(1));
        headings.push({ level, text });
        lines.push(`${'#'.repeat(level)} ${text}`);
      } else if (tag === 'LI') {
        lines.push(`- ${text}`);
      } else if (tag === 'BLOCKQUOTE') {
        lines.push(`> ${text}`);
      } else {
        lines.push(text);
      }
    }
    node = walker.nextNode();
  }

  const content = lines.join('\n\n').trim();
  return {
    url: window.location.href,
    final_url: window.location.href,
    title: document.title || '',
    description: meta('description'),
    canonical: canonical ? canonical.href : null,
    content_markdown: content,
    headings,
    word_count: content ? content.split(/\s+/).filter(Boolean).length : 0,
  };
})()
"""


async def extract_article(session_id: str) -> dict[str, Any]:
    client, _ = await _with_page_session(session_id)
    try:
        data = await client.evaluate(ARTICLE_JS, await_promise=False)
        if not isinstance(data, dict):
            raise RuntimeError("Article extraction returned unexpected payload")
        data["command"] = "extract"
        data["mode"] = "article"
        data["fetched_at"] = datetime.now(timezone.utc).isoformat()
        data["error"] = None
        return data
    finally:
        await client.close()


def article_error(message: str, code: str = "extract") -> dict[str, Any]:
    return {
        "command": "extract",
        "mode": "article",
        "error": {"code": code, "message": message},
    }
