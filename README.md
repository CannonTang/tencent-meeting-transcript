# Tencent Meeting Transcript

用于抓取腾讯会议已经生成的逐字稿，并导出为带发言人和时间戳的 Markdown 文件。支持公开分享页，也支持用户在已连接 Chrome 中自行登录并获授权查看的录制页面。

## 功能

- 支持 `meeting.tencent.com/meeting-record/shares` 公开分享链接。
- 支持在用户已登录、已授权的 Chrome 会话中读取 `meeting.tencent.com/cw/`、`meeting.tencent.com/crm/` 等受限录制页面。
- 直接获取页面已有逐字稿，自动处理分页和重复段落。
- 不下载录像、不进行音频转写、不绕过密码、登录或审批限制，也不读取或导出浏览器 Cookie、Token、密码等凭据。

## 使用

将技能目录放入 `~/.codex/skills/` 后，可让 Codex 使用 `$tencent-meeting-transcript` 处理链接；也可直接运行：

```bash
python3 scripts/fetch_transcript.py '<腾讯会议分享链接>' \
  --out "$HOME/Desktop/meeting_transcript.md"
```

输出文件会保留腾讯会议原有的发言人标签与时间戳。页面逐字稿本身可能存在识别误差，请按需人工核对。

## 需要登录的录制

先在 Chrome 中自行登录拥有查看权限的腾讯会议账号，并连接该 Chrome 会话。然后向 Codex 提供录制链接；技能会在该已授权页面中切换到“逐字稿”视图、分段滚动读取内容并导出 Markdown。

登录、短信验证、密码、审批或验证码必须由用户自行在浏览器中完成。技能不会读取、保存或传递浏览器的 Cookie、Token、密码或其他登录凭据。
