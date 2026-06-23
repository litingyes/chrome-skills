# Search recipe

One-shot Google search. Equivalent manual composition:

```bash
SESSION=$(skills/chrome/scripts/cdp launch | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
skills/chrome/scripts/cdp navigate --session "$SESSION" --url "https://www.google.com/search?q=QUERY&hl=en" --wait load
skills/chrome/scripts/cdp wait --session "$SESSION" --networkidle
skills/chrome/scripts/extract serp --session "$SESSION" --limit 10
skills/chrome/scripts/cdp close --session "$SESSION"
```

## CLI

```bash
skills/chrome/scripts/search "python asyncio"
skills/chrome/scripts/search "python asyncio" --limit 5 --lang en
skills/chrome/scripts/search "python asyncio" --headed --user-data-dir "/path/to/chrome/profile"
skills/chrome/scripts/search "python asyncio" --timeout-ms 30000
```

## Output

See [output-schemas.md](output-schemas.md#search).

## CAPTCHA / bot check

Headless Chrome often triggers Google reCAPTCHA. When this happens:

- JSON includes `error.code=captcha` and `error.remediation`
- Retry with a real profile and headed mode:

```bash
skills/chrome/scripts/search "python asyncio" \
  --headed \
  --user-data-dir "$HOME/Library/Application Support/Google/Chrome"
```

Or compose manually with `cdp` + `extract serp` so you can inspect the page between steps.

## Notes

- Engine is Google only (no automatic fallback to other search engines).
- Consent banners are not guaranteed to be dismissed in v1; headed + profile is the reliable path.
