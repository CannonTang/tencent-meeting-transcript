# Tencent Meeting Transcript

用于抓取腾讯会议公开录制分享页中已经生成的逐字稿，并导出为带发言人和时间戳的 Markdown 文件。

## 功能

- 支持 `meeting.tencent.com/meeting-record/shares` 公开分享链接。
- 直接获取页面已有逐字稿，自动处理分页和重复段落。
- 不下载录像、不进行音频转写、不绕过密码、登录或审批限制。

## 使用

将技能目录放入 `~/.codex/skills/` 后，可让 Codex 使用 `$tencent-meeting-transcript` 处理链接；也可直接运行：

```bash
python3 scripts/fetch_transcript.py '<腾讯会议分享链接>' \
  --out "$HOME/Desktop/meeting_transcript.md"
```

输出文件会保留腾讯会议原有的发言人标签与时间戳。页面逐字稿本身可能存在识别误差，请按需人工核对。
