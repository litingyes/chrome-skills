"""Layout extraction and UI rule checks from the current page."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .cdp import _with_page_session

DEFAULT_SELECTORS = [
    "main",
    "nav",
    "header",
    "footer",
    "article",
    "h1",
    "h2",
    "h3",
    "p",
    "button",
    "a[href]",
    "[data-testid]",
]

DEFAULT_RULES = ["spacing", "alignment", "overflow", "touch-target", "blank"]

LAYOUT_JS_TEMPLATE = r"""
(() => {
  const config = %CONFIG%;
  const enabledRules = new Set(config.rules || []);
  const selectors = config.selectors || [];
  const GRID = 4;
  const gridTolerance = 1;

  const round = (n) => Math.round(n * 10) / 10;
  const px = (v) => parseFloat(v) || 0;

  const simpleSelector = (el) => {
    if (el.id) return `#${CSS.escape(el.id)}`;
    const testId = el.getAttribute('data-testid');
    if (testId) return `[data-testid="${testId}"]`;
    const tag = el.tagName.toLowerCase();
    const role = el.getAttribute('role');
    if (role) return `${tag}[role="${role}"]`;
    const parent = el.parentElement;
    if (parent) {
      const siblings = [...parent.children].filter((c) => c.tagName === el.tagName);
      if (siblings.length > 1) {
        const idx = siblings.indexOf(el) + 1;
        return `${tag}:nth-of-type(${idx})`;
      }
    }
    return tag;
  };

  const isVisible = (el) => {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return (
      style.display !== 'none' &&
      style.visibility !== 'hidden' &&
      parseFloat(style.opacity) > 0 &&
      rect.width > 0 &&
      rect.height > 0
    );
  };

  const docEl = document.documentElement;
  const body = document.body;
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight,
    scrollWidth: docEl.scrollWidth,
    scrollHeight: docEl.scrollHeight,
  };

  const bodyScrollWidth = body ? body.scrollWidth : docEl.scrollWidth;
  const overflow = {
    horizontal:
      docEl.scrollWidth > docEl.clientWidth + 1 ||
      bodyScrollWidth > window.innerWidth + 1,
    vertical: docEl.scrollHeight > docEl.clientHeight + 1,
  };

  const seen = new Set();
  const elements = [];

  for (const sel of selectors) {
    let matched;
    try {
      matched = document.querySelectorAll(sel);
    } catch (_) {
      continue;
    }
    matched.forEach((el) => {
      if (seen.has(el)) return;
      seen.add(el);
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 && rect.height === 0) return;
      const style = window.getComputedStyle(el);
      elements.push({
        selector: sel,
        path: simpleSelector(el),
        role: el.getAttribute('role') || el.tagName.toLowerCase(),
        box: {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          width: Math.round(rect.width),
          height: Math.round(rect.height),
        },
        styles: {
          marginTop: style.marginTop,
          marginBottom: style.marginBottom,
          marginLeft: style.marginLeft,
          marginRight: style.marginRight,
          paddingTop: style.paddingTop,
          paddingLeft: style.paddingLeft,
          fontSize: style.fontSize,
          lineHeight: style.lineHeight,
        },
        visible: isVisible(el),
      });
    });
  }

  const pairs = [];
  const root = document.querySelector('main') || document.body;
  if (root) {
    const blocks = [...root.querySelectorAll('h1,h2,h3,h4,h5,h6,p,section,article,li')]
      .filter(isVisible)
      .map((el) => ({ el, rect: el.getBoundingClientRect() }))
      .sort((a, b) => a.rect.top - b.rect.top || a.rect.left - b.rect.left);

    for (let i = 0; i < blocks.length - 1; i += 1) {
      const a = blocks[i];
      const b = blocks[i + 1];
      const gap = round(b.rect.top - a.rect.bottom);
      if (gap < 0 || gap > 500) continue;
      const axis =
        Math.abs(a.rect.left - b.rect.left) < 8 ? 'vertical' : 'horizontal';
      pairs.push({
        a: simpleSelector(a.el),
        b: simpleSelector(b.el),
        gap,
        axis,
      });
    }
  }

  const issues = [];

  const onGrid = (value) => {
    const rem = Math.abs(value % GRID);
    return rem <= gridTolerance || rem >= GRID - gridTolerance;
  };

  if (enabledRules.has('overflow') && overflow.horizontal) {
    issues.push({
      rule: 'overflow.horizontal',
      severity: 'error',
      message: `Horizontal overflow detected (scrollWidth ${viewport.scrollWidth}px > viewport ${viewport.width}px)`,
      selector: null,
    });
  }

  if (enabledRules.has('spacing')) {
    for (const pair of pairs) {
      if (pair.axis !== 'vertical') continue;
      const aTagName = pair.a.split(':')[0].split('[')[0];
      if (/^h[1-6]$/i.test(aTagName)) {
        const headingEl = [...root.querySelectorAll('h1,h2,h3,h4,h5,h6')].find(
          (el) => simpleSelector(el) === pair.a,
        );
        if (headingEl && pair.gap < 12) {
          issues.push({
            rule: 'spacing.below-heading',
            severity: 'warn',
            message: `${pair.a} → ${pair.b} gap ${pair.gap}px, expected >= 12px`,
            selector: pair.a,
          });
        }
      }
      if (pair.gap > 0 && pair.gap < 48 && !onGrid(pair.gap)) {
        issues.push({
          rule: 'spacing.grid',
          severity: 'info',
          message: `${pair.a} → ${pair.b} gap ${pair.gap}px is off ${GRID}px grid`,
          selector: pair.a,
        });
      }
    }

    for (const item of elements) {
      const mb = px(item.styles.marginBottom);
      const mt = px(item.styles.marginTop);
      for (const val of [mb, mt]) {
        if (val > 0 && val < 48 && !onGrid(val)) {
          issues.push({
            rule: 'spacing.margin-grid',
            severity: 'info',
            message: `${item.path} margin ${val}px is off ${GRID}px grid`,
            selector: item.path,
          });
        }
      }
    }
  }

  if (enabledRules.has('alignment')) {
    const groups = new Map();
    document.querySelectorAll('ul, ol, [class*="grid"], [class*="flex"], [class*="card"]').forEach((parent) => {
      const children = [...parent.children].filter(isVisible);
      if (children.length < 2) return;
      const rects = children.map((el) => el.getBoundingClientRect());
      const lefts = rects.map((r) => Math.round(r.left));
      const variance = Math.max(...lefts) - Math.min(...lefts);
      if (variance > 4 && variance < 200) {
        const key = simpleSelector(parent);
        groups.set(key, { parent: key, variance, count: children.length });
      }
    });
    for (const [, group] of groups) {
      issues.push({
        rule: 'alignment.siblings',
        severity: 'warn',
        message: `Children of ${group.parent} left-edge variance ${group.variance}px across ${group.count} items`,
        selector: group.parent,
      });
    }
  }

  if (enabledRules.has('touch-target')) {
    const clickables = document.querySelectorAll(
      'button, a[href], [role="button"], input[type="submit"], input[type="button"], [onclick]',
    );
    clickables.forEach((el) => {
      if (!isVisible(el)) return;
      const rect = el.getBoundingClientRect();
      const minSize = Math.min(rect.width, rect.height);
      if (minSize > 0 && minSize < 44) {
        issues.push({
          rule: 'touch-target.size',
          severity: 'warn',
          message: `Touch target ${Math.round(minSize)}px < 44px minimum`,
          selector: simpleSelector(el),
        });
      }
    });
  }

  if (enabledRules.has('blank')) {
    const main = document.querySelector('main') || document.body;
    if (main) {
      const rect = main.getBoundingClientRect();
      const area = rect.width * rect.height;
      const textLen = (main.innerText || '').trim().length;
      if (area > 50000 && textLen < 20) {
        issues.push({
          rule: 'blank.main-content',
          severity: 'warn',
          message: `Main content area appears empty (${textLen} chars in ${Math.round(area)}px²)`,
          selector: simpleSelector(main),
        });
      }
    }
  }

  const fixedEls = [...document.querySelectorAll('*')].filter((el) => {
    const style = window.getComputedStyle(el);
    return style.position === 'fixed' || style.position === 'sticky';
  });
  const mainRect = (document.querySelector('main') || document.body)?.getBoundingClientRect();
  if (mainRect && enabledRules.has('overflow')) {
    fixedEls.forEach((el) => {
      if (!isVisible(el)) return;
      const rect = el.getBoundingClientRect();
      const overlaps =
        rect.bottom > mainRect.top + 40 &&
        rect.top < mainRect.bottom - 40 &&
        rect.width > window.innerWidth * 0.5;
      if (overlaps && rect.height > 60) {
        issues.push({
          rule: 'overflow.fixed-overlay',
          severity: 'info',
          message: `Fixed/sticky element ${simpleSelector(el)} may obscure main content`,
          selector: simpleSelector(el),
        });
      }
    });
  }

  return { viewport, overflow, elements, pairs, issues };
})()
"""


def _build_layout_js(
    selectors: list[str] | None,
    rules: list[str] | None,
) -> str:
    config = {
        "selectors": selectors or DEFAULT_SELECTORS,
        "rules": rules or DEFAULT_RULES,
    }
    return LAYOUT_JS_TEMPLATE.replace("%CONFIG%", json.dumps(config))


async def extract_layout(
    session_id: str,
    *,
    selectors: list[str] | None = None,
    rules: list[str] | None = None,
) -> dict[str, Any]:
    client, _ = await _with_page_session(session_id)
    try:
        expression = _build_layout_js(selectors, rules)
        data = await client.evaluate(expression, await_promise=False)
        if not isinstance(data, dict):
            raise RuntimeError("Layout extraction returned unexpected payload")
        return {
            "command": "extract",
            "mode": "layout",
            "viewport": data.get("viewport", {}),
            "overflow": data.get("overflow", {}),
            "elements": data.get("elements", []),
            "pairs": data.get("pairs", []),
            "issues": data.get("issues", []),
            "issue_count": len(data.get("issues", [])),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "error": None,
        }
    finally:
        await client.close()
