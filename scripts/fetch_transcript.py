#!/usr/bin/env python3
"""Fetch Tencent Meeting's page-provided transcript from a public share URL."""

from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
API_URL = "https://meeting.tencent.com/wemeet-cloudrecording-webapi/v1/minutes/detail"


class TranscriptError(RuntimeError):
    pass


def fetch(url: str, referer: str | None = None) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    if referer:
        headers["Referer"] = referer
    try:
        with urlopen(Request(url, headers=headers), timeout=30) as response:
            return response.read()
    except HTTPError as error:
        raise TranscriptError(f"Request failed with HTTP {error.code}: {url}") from error
    except URLError as error:
        raise TranscriptError(f"Network request failed: {error.reason}") from error


def get_share_id(share_url: str) -> str:
    parsed = urlparse(share_url)
    if parsed.netloc != "meeting.tencent.com" or not parsed.path.endswith("/shares"):
        raise TranscriptError("Expected a meeting.tencent.com/meeting-record/shares URL.")
    share_id = parse_qs(parsed.query).get("id", [""])[0]
    if not share_id:
        raise TranscriptError("The share URL does not contain an id parameter.")
    return share_id


def extract_record_info(page: str) -> tuple[str, str, str]:
    # The Next.js payload serializes data as escaped JSON inside script tags.
    meeting_ids = re.findall(r'\\?"meeting_id\\?"\s*:\\?"(\d+)\\?"', page)
    if not meeting_ids:
        raise TranscriptError("Could not find the meeting id in the public share page.")
    recording = re.search(
        r'\\?"recordings\\?"\s*:\s*\[\{.*?\\?"id\\?"\s*:\\?"(\d+)\\?"',
        page,
        re.DOTALL,
    )
    if not recording:
        raise TranscriptError("Could not find the recording id in the public share page.")
    subject = re.findall(r'\\?"subject\\?"\s*:\\?"([^"\\]+)\\?"', page)
    title = "Tencent Meeting Transcript"
    if subject:
        try:
            title = base64.b64decode(subject[-1]).decode("utf-8")
        except Exception:
            pass
    return meeting_ids[-1], recording.group(1), title


def request_minutes(share_url: str, params: dict[str, str]) -> dict[str, Any]:
    raw = fetch(f"{API_URL}?{urlencode(params)}", referer=share_url)
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as error:
        raise TranscriptError("Transcript endpoint did not return JSON.") from error
    if result.get("code") != 0:
        message = result.get("msg") or result.get("err_detail") or "unknown error"
        raise TranscriptError(f"Tencent Meeting did not allow transcript retrieval: {message}")
    if not result.get("minutes", {}).get("paragraphs"):
        raise TranscriptError("No transcript paragraphs are available for this recording.")
    return result


def timestamp(milliseconds: int) -> str:
    seconds = max(0, milliseconds // 1000)
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def paragraph_text(paragraph: dict[str, Any]) -> str:
    sentences = []
    for sentence in paragraph.get("sentences", []):
        text = "".join(word.get("text", "") for word in sentence.get("words", []))
        if text:
            sentences.append(text)
    return "\n\n".join(sentences)


def render_markdown(title: str, paragraphs: list[dict[str, Any]]) -> str:
    blocks = [
        f"# {title}",
        "腾讯会议公开分享页逐字稿。文本由页面已有的逐字稿接口获取，未使用音频转写。",
    ]
    for paragraph in paragraphs:
        speaker = paragraph.get("speaker", {}).get("user_name") or "未知发言人"
        text = paragraph_text(paragraph)
        if text:
            blocks.append(f"### [{timestamp(int(paragraph.get('start_time', 0)))}] {speaker}\n\n{text}")
    return "\n\n".join(blocks) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("share_url", help="Public Tencent Meeting recording share URL")
    parser.add_argument("--out", type=Path, required=True, help="Markdown output path")
    args = parser.parse_args()
    try:
        share_id = get_share_id(args.share_url)
        page = html.unescape(fetch(args.share_url).decode("utf-8", errors="replace"))
        meeting_id, recording_id, title = extract_record_info(page)
        base = {
            "id": share_id,
            "pwd": "",
            "activity_uid": "",
            "page_source": "record",
            "meeting_id": meeting_id,
            "recording_id": recording_id,
            "lang": "zh",
            "minutes_version": "0",
            "return_ori_minutes_translating": "1",
            "return_ori": "0",
        }
        response = request_minutes(args.share_url, base | {"limit": "20", "start_pid": "0", "fview": "1"})
        paragraphs = response["minutes"]["paragraphs"]
        while response.get("more"):
            last_pid = paragraphs[-1].get("pid")
            if last_pid is None:
                raise TranscriptError("Transcript pagination response has no paragraph id.")
            response = request_minutes(args.share_url, base | {"pid": str(last_pid), "fview": "0"})
            paragraphs.extend(response["minutes"]["paragraphs"])
        deduped = {str(item.get("pid")): item for item in paragraphs}
        ordered = sorted(deduped.values(), key=lambda item: int(item.get("start_time", 0)))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render_markdown(title, ordered), encoding="utf-8")
        print(f"Wrote {len(ordered)} transcript paragraphs to {args.out}")
        return 0
    except TranscriptError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
