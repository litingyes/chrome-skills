"""Chrome binary discovery and launch argument assembly."""

from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path


def find_chrome_executable() -> str:
    system = platform.system()
    candidates: list[str] = []

    if system == "Darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        ]
    elif system == "Linux":
        candidates = [
            "google-chrome-stable",
            "google-chrome",
            "chromium-browser",
            "chromium",
            "chrome",
        ]
    elif system == "Windows":
        program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        program_files_x86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
        candidates = [
            os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(program_files, "Chromium", "Application", "chrome.exe"),
        ]
    else:
        candidates = ["google-chrome", "chromium", "chrome"]

    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved

    raise FileNotFoundError(
        "Chrome or Chromium not found. Install Google Chrome or set CHROME_PATH."
    )


def resolve_chrome_executable() -> str:
    override = os.environ.get("CHROME_PATH")
    if override:
        path = Path(override)
        if not path.exists():
            raise FileNotFoundError(f"CHROME_PATH does not exist: {override}")
        return str(path)
    return find_chrome_executable()


def build_launch_args(
    *,
    port: int,
    user_data_dir: str,
    headed: bool = False,
    viewport: tuple[int, int] | None = None,
) -> list[str]:
    chrome = resolve_chrome_executable()
    args = [
        chrome,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-translate",
        "--disable-features=TranslateUI",
        "--disable-blink-features=AutomationControlled",
    ]

    if not headed:
        args.append("--headless=new")

    args.extend(
        [
            "--disable-gpu",
            "--hide-scrollbars",
            "--mute-audio",
        ]
    )

    if viewport:
        width, height = viewport
        args.append(f"--window-size={width},{height}")

    return args
