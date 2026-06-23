"""Minimal Chrome DevTools Protocol client."""

from __future__ import annotations

import asyncio
import json
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from . import session as session_store
from .chrome import build_launch_args


class CDPError(RuntimeError):
    pass


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _http_get_json(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def _wait_for_devtools(port: int, timeout_s: float = 15.0) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            return _http_get_json(f"http://127.0.0.1:{port}/json/version")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(0.1)
    raise CDPError(f"DevTools did not become ready on port {port}: {last_error}")


def _create_target(port: int, url: str = "about:blank") -> dict[str, Any]:
    encoded = urllib.parse.quote(url, safe="")
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/json/new?{encoded}",
        method="PUT",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _list_targets(port: int) -> list[dict[str, Any]]:
    data = _http_get_json(f"http://127.0.0.1:{port}/json/list")
    if isinstance(data, list):
        return data
    return []


class CDPSession:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self._ws: Any = None
        self._next_id = 1
        self._pending: dict[int, asyncio.Future[Any]] = {}

    async def connect(self) -> None:
        import websockets

        self._ws = await websockets.connect(
            self.ws_url,
            max_size=50 * 1024 * 1024,
            open_timeout=15,
        )
        asyncio.create_task(self._reader())

    async def close(self) -> None:
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def _reader(self) -> None:
        assert self._ws is not None
        async for raw in self._ws:
            message = json.loads(raw)
            if "id" in message:
                future = self._pending.pop(message["id"], None)
                if future and not future.done():
                    if "error" in message:
                        future.set_exception(CDPError(json.dumps(message["error"])))
                    else:
                        future.set_result(message.get("result", {}))

    async def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        if self._ws is None:
            raise CDPError("CDP session is not connected")
        message_id = self._next_id
        self._next_id += 1
        payload = {"id": message_id, "method": method, "params": params or {}}
        future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        self._pending[message_id] = future
        await self._ws.send(json.dumps(payload))
        return await asyncio.wait_for(future, timeout=60)

    async def evaluate(
        self,
        expression: str,
        *,
        await_promise: bool = True,
        return_by_value: bool = True,
    ) -> Any:
        result = await self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": await_promise,
                "returnByValue": return_by_value,
            },
        )
        if result.get("exceptionDetails"):
            raise CDPError(json.dumps(result["exceptionDetails"]))
        return result.get("result", {}).get("value")

    async def navigate(self, url: str) -> None:
        await self.call("Page.enable")
        await self.call("Runtime.enable")
        await self.call("Page.navigate", {"url": url})

    async def wait_for_load(self, timeout_ms: int = 25000) -> None:
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            state = await self.evaluate("document.readyState", await_promise=False)
            if state in ("interactive", "complete"):
                return
            await asyncio.sleep(0.1)
        raise CDPError(f"Timed out waiting for load after {timeout_ms}ms")

    async def wait_network_idle(self, timeout_ms: int = 25000, idle_ms: int = 500) -> None:
        deadline = time.time() + timeout_ms / 1000
        last_busy = time.time()
        while time.time() < deadline:
            busy = await self.evaluate(
                """
                (() => {
                  const entries = performance.getEntriesByType('resource');
                  const recent = entries.filter(e => e.responseEnd === 0 || (performance.now() - e.responseEnd) < 500);
                  return recent.length;
                })()
                """,
                await_promise=False,
            )
            if int(busy or 0) == 0:
                if (time.time() - last_busy) * 1000 >= idle_ms:
                    return
            else:
                last_busy = time.time()
            await asyncio.sleep(0.1)
        raise CDPError(f"Timed out waiting for network idle after {timeout_ms}ms")

    async def wait_for_selector(self, selector: str, timeout_ms: int = 25000) -> None:
        deadline = time.time() + timeout_ms / 1000
        expr = json.dumps(selector)
        while time.time() < deadline:
            found = await self.evaluate(
                f"Boolean(document.querySelector({expr}))",
                await_promise=False,
            )
            if found:
                return
            await asyncio.sleep(0.1)
        raise CDPError(f"Timed out waiting for selector {selector}")

    async def wait_for_text(self, text: str, timeout_ms: int = 25000) -> None:
        deadline = time.time() + timeout_ms / 1000
        expr = json.dumps(text)
        while time.time() < deadline:
            found = await self.evaluate(
                f"document.body && document.body.innerText.includes({expr})",
                await_promise=False,
            )
            if found:
                return
            await asyncio.sleep(0.1)
        raise CDPError(f"Timed out waiting for text: {text}")

    async def current_url(self) -> str:
        value = await self.evaluate("window.location.href", await_promise=False)
        return str(value or "")

    async def snapshot(self, include_html: bool = False) -> dict[str, Any]:
        title = await self.evaluate("document.title", await_promise=False)
        url = await self.current_url()
        payload: dict[str, Any] = {
            "title": title or "",
            "url": url,
        }
        if include_html:
            payload["html"] = await self.evaluate(
                "document.documentElement.outerHTML",
                await_promise=False,
            )
        else:
            html_len = await self.evaluate(
                "document.documentElement.outerHTML.length",
                await_promise=False,
            )
            payload["html_length"] = int(html_len or 0)
        return payload


async def _with_page_session(session_id: str) -> tuple[CDPSession, dict[str, Any]]:
    record = session_store.load_session(session_id)
    page_ws_url = record.get("page_ws_url")
    if not page_ws_url:
        raise CDPError(f"Session {session_id} has no active page target")
    client = CDPSession(page_ws_url)
    await client.connect()
    return client, record


async def launch_browser(
    *,
    headed: bool = False,
    user_data_dir: str | None = None,
    viewport: tuple[int, int] | None = None,
) -> dict[str, Any]:
    port = find_free_port()
    profile_dir = user_data_dir or tempfile.mkdtemp(prefix="chrome-skill-")
    args = build_launch_args(
        port=port,
        user_data_dir=profile_dir,
        headed=headed,
        viewport=viewport,
    )
    proc = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    version = _wait_for_devtools(port)
    target = _create_target(port, "about:blank")
    page_ws_url = target.get("webSocketDebuggerUrl")
    if not page_ws_url:
        proc.terminate()
        raise CDPError("Failed to create initial page target")

    record = session_store.create_session_record(
        pid=proc.pid,
        port=port,
        ws_url=version.get("webSocketDebuggerUrl", ""),
        user_data_dir=profile_dir,
        headed=headed,
        page_ws_url=page_ws_url,
    )
    return {
        "command": "cdp",
        "action": "launch",
        "session_id": record["session_id"],
        "port": port,
        "headed": headed,
        "error": None,
    }


async def navigate_page(
    session_id: str,
    url: str,
    *,
    wait: str | None = "load",
    timeout_ms: int = 25000,
) -> dict[str, Any]:
    client, record = await _with_page_session(session_id)
    try:
        await client.navigate(url)
        if wait == "load":
            await client.wait_for_load(timeout_ms=timeout_ms)
        elif wait == "networkidle":
            await client.wait_for_load(timeout_ms=timeout_ms)
            await client.wait_network_idle(timeout_ms=timeout_ms)
        final_url = await client.current_url()
        return {
            "command": "cdp",
            "action": "navigate",
            "session_id": session_id,
            "url": url,
            "final_url": final_url,
            "wait": wait,
            "error": None,
        }
    finally:
        await client.close()


async def wait_page(
    session_id: str,
    *,
    load: bool = False,
    networkidle: bool = False,
    selector: str | None = None,
    text: str | None = None,
    timeout_ms: int = 25000,
) -> dict[str, Any]:
    client, _ = await _with_page_session(session_id)
    try:
        if load:
            await client.wait_for_load(timeout_ms=timeout_ms)
        if networkidle:
            await client.wait_network_idle(timeout_ms=timeout_ms)
        if selector:
            await client.wait_for_selector(selector, timeout_ms=timeout_ms)
        if text:
            await client.wait_for_text(text, timeout_ms=timeout_ms)
        return {
            "command": "cdp",
            "action": "wait",
            "session_id": session_id,
            "error": None,
        }
    finally:
        await client.close()


async def evaluate_page(
    session_id: str,
    expression: str,
    *,
    await_promise: bool = True,
) -> dict[str, Any]:
    client, _ = await _with_page_session(session_id)
    try:
        value = await client.evaluate(expression, await_promise=await_promise)
        return {
            "command": "cdp",
            "action": "evaluate",
            "session_id": session_id,
            "value": value,
            "error": None,
        }
    finally:
        await client.close()


async def snapshot_page(
    session_id: str,
    *,
    include_html: bool = False,
) -> dict[str, Any]:
    client, _ = await _with_page_session(session_id)
    try:
        data = await client.snapshot(include_html=include_html)
        return {
            "command": "cdp",
            "action": "snapshot",
            "session_id": session_id,
            **data,
            "error": None,
        }
    finally:
        await client.close()


def close_browser_session(session_id: str | None = None, close_all: bool = False) -> dict[str, Any]:
    if close_all:
        closed = session_store.close_all_sessions()
        return {
            "command": "cdp",
            "action": "close",
            "closed": closed,
            "error": None,
        }
    if not session_id:
        raise CDPError("session_id is required unless --all is set")
    result = session_store.close_session(session_id)
    return {
        "command": "cdp",
        "action": "close",
        **result,
        "error": None,
    }
