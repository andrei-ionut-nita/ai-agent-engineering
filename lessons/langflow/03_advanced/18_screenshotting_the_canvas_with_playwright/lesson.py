"""
Lesson 18: driving Langflow's own UI with Playwright, exactly the
pattern this course's `lessons/playwright` course teaches, aimed at
Langflow's own canvas instead of an arbitrary website. Every
`canvas.png` in this course was produced this way.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1, and
LANGFLOW_API_KEY must be set, see Lesson 7's README):

    uv run python lessons/langflow/03_advanced/18_screenshotting_the_canvas_with_playwright/lesson.py
"""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

LANGFLOW_URL = "http://127.0.0.1:7860"
HEADERS = {"x-api-key": os.environ["LANGFLOW_API_KEY"]}
FLOW_PATH = Path(__file__).parent.parent.parent / "01_beginner" / "02_first_flow" / "flow.json"
OUTPUT_DIR = Path(__file__).parent


def upload_flow() -> str:
    with FLOW_PATH.open("rb") as f:
        response = httpx.post(
            f"{LANGFLOW_URL}/api/v1/flows/upload/",
            headers=HEADERS,
            files={"file": ("flow.json", f, "application/json")},
        )
    response.raise_for_status()
    return response.json()[0]["id"]


def screenshot_flow(flow_id: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    screenshot_path = OUTPUT_DIR / "canvas.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(f"{LANGFLOW_URL}/flow/{flow_id}")
        # Wait for at least one component node to actually render before
        # capturing, the canvas is a React app, the URL resolving doesn't
        # mean the graph has painted yet.
        page.wait_for_selector('[data-testid^="rf__node-"]', timeout=15000)
        # The canvas opens at whatever zoom level it was last saved at,
        # "Zoom To Fit" (Ctrl+1) frames every node before capturing.
        page.keyboard.press("Control+1")
        page.wait_for_timeout(500)
        page.screenshot(path=screenshot_path)
        browser.close()
    return screenshot_path


def delete_flow(flow_id: str) -> None:
    httpx.delete(f"{LANGFLOW_URL}/api/v1/flows/{flow_id}", headers=HEADERS).raise_for_status()


def main() -> None:
    flow_id = upload_flow()
    path = screenshot_flow(flow_id)
    print(f"Canvas screenshot saved to: {path}")
    print(f"File size: {path.stat().st_size} bytes")
    delete_flow(flow_id)


if __name__ == "__main__":
    main()
