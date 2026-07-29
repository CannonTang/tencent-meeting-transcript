---
name: tencent-meeting-transcript
description: Fetch and format the page-provided transcript from a public Tencent Meeting recording share URL. Use when the user supplies a meeting.tencent.com/meeting-record/shares link and asks for its transcript, verbatim record, speaker/timestamp text, or a Markdown export without audio transcription. Do not use to bypass a password, login, approval, or other access restriction.
---

# Tencent Meeting Transcript

Use this skill only for a share page that is already viewable through the supplied link. Retrieve Tencent Meeting's existing transcript data; do not download media or run ASR.

## Workflow

1. Run the bundled script with the original share URL and an output Markdown path.

   ```bash
   python3 "$HOME/.codex/skills/tencent-meeting-transcript/scripts/fetch_transcript.py" \
     '<SHARE_URL>' \
     --out "$HOME/Desktop/tencent_meeting_transcript.md"
   ```

2. Inspect the reported paragraph count and the beginning, middle, and end of the Markdown file. Infer the approximate coverage from the last timestamp.
3. State that the output is Tencent Meeting's existing machine transcript and may contain recognition errors. Preserve speaker labels and timestamps. Do not silently rewrite content.

## Access Boundaries

- Stop when the page or API reports a password, login, approval, expired link, or missing transcript. Tell the user what access is needed.
- Do not use browser cookies from an unrelated user profile, CAPTCHA solving, credential extraction, or endpoint variations to evade access controls.
- The script intentionally supports only public cloud-recording share pages. It does not work on local files or meeting links without a recording transcript.

## Deliverables

- Default output: a UTF-8 Markdown file with `### [HH:MM:SS] speaker` headings and paragraph text.
- Use the user-requested output location. For a simple request, default to the Desktop and name the file from the meeting title when practical.
