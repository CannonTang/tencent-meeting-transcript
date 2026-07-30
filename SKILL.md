---
name: tencent-meeting-transcript
description: Fetch and format Tencent Meeting's existing transcript from a public share page or, with the user's already-authorized Chrome session, an account-permitted recording page. Use when the user asks for a Tencent Meeting transcript, verbatim record, speaker/timestamp text, or Markdown export without audio transcription. Do not bypass a password, login, approval, or other access restriction.
---

# Tencent Meeting Transcript

Retrieve Tencent Meeting's existing transcript data; do not download media or run ASR. Select one of the following access paths.

## Workflow

### Public share page

For an already-viewable `meeting.tencent.com/meeting-record/shares` URL, run the bundled script with the original share URL and an output Markdown path.

```bash
python3 "$HOME/.codex/skills/tencent-meeting-transcript/scripts/fetch_transcript.py" \
  '<SHARE_URL>' \
  --out "$HOME/Desktop/tencent_meeting_transcript.md"
```

Inspect the reported paragraph count and the beginning, middle, and end of the Markdown file. Infer the approximate coverage from the last timestamp.

### Account-permitted recording

For a recording page that requires the user's Tencent Meeting account, such as a `meeting.tencent.com/cw/` or `meeting.tencent.com/crm/` URL:

1. Use the Chrome-control surface only when the user has connected Chrome and has personally signed in to the Tencent Meeting account that can view the recording. Do not ask for credentials.
2. If Chrome is not connected, or the page asks for sign-in, SMS verification, a password, approval, or a CAPTCHA, stop and ask the user to complete that step in Chrome, then confirm it is ready.
3. In the authorized page, open the `逐字稿` view. Read the page-provided speaker, timestamp, and text. These pages use a virtual scrolling transcript list, so scroll in overlapping, rendered increments and deduplicate overlapping paragraphs.
4. Export the collected paragraphs to UTF-8 Markdown using `### [HH:MM:SS] speaker` headings. Inspect the beginning, middle, and end and report the paragraph count and final timestamp.
5. State that the output is Tencent Meeting's existing machine transcript and may contain recognition errors. Preserve speaker labels and timestamps. Do not silently rewrite content.

## Access Boundaries

- Stop when the page or API reports a password, login, approval, expired link, CAPTCHA, or missing transcript. Tell the user what access is needed.
- Never inspect, export, print, persist, or reuse browser cookies, passwords, tokens, local storage, or profile data. Do not use another user's browser profile, credential extraction, CAPTCHA solving, or endpoint variations to evade access controls.
- The bundled Python script intentionally supports only public cloud-recording share pages. Account-permitted recordings must be read through the user's currently authorized Chrome page, not by copying its session into an HTTP client.
- This skill does not work on local files or recording pages without an existing Tencent Meeting transcript.

## Deliverables

- Default output: a UTF-8 Markdown file with `### [HH:MM:SS] speaker` headings and paragraph text.
- Use the user-requested output location. For a simple request, default to the Desktop and name the file from the meeting title when practical.
