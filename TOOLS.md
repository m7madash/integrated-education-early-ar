# Telegram Bot Configuration

Bot Token: 8785223240:AAG8Vj4EjCmdDgYtfuho-PGttFzluv-DIFw

## Usage
This token should be configured in OpenClaw to enable Telegram messaging.

---

<!-- BEGIN:kilo-cli -->
## Kilo CLI

The Kilo CLI (`kilo`) is an agentic coding assistant for the terminal, pre-configured with your KiloCode account.

- Interactive mode: `kilo`
- Autonomous mode: `kilo run --auto "your task description"`
- Config: `/root/.config/kilo/opencode.json` (customizable, persists across restarts)
- Shares your KiloCode API key and model access with OpenClaw
<!-- END:kilo-cli -->

---

<!-- BEGIN:github -->
## GitHub Configuration

Repository: `m7madash/Abduallh-projects`
Remote URL: `https://github.com/m7madash/Abduallh-projects.git`
Authentication: GitHub PAT (Personal Access Token) stored in git remote URL (recommended: use credential helper or SSH for production)

## Notes
- Token has `repo` scope (full control of private/public repositories).
- If token expires or needs rotation, update remote: `git remote set-url origin https://<NEW_TOKEN>@github.com/m7madash/Abduallh-projects.git`
- For security, consider switching to SSH keys: `git remote set-url origin git@github.com:m7madash/Abduallh-projects.git`
<!-- END:github -->