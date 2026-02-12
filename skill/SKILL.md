---
name: clawpet
description: "OpenClaw pet companion skill. Manage adopted pets, run interactions, and produce pet image prompts."
metadata:
  openclaw:
    requires:
      anyBins: [clawpet, uv, uvx]
    install:
      - id: clawpet-git
        kind: pip
        package: "git+https://github.com/yazelin/clawpet.git"
        bins: [clawpet]
        label: "Install clawpet from GitHub"
---

# clawpet — OpenClaw Pet Companion 🐾

Use this skill when the user wants to adopt a pet, check pet status, interact with the pet, or send a pet image.
Pet status includes passive time-based updates, so each check-in can reflect elapsed time.

## Typical triggers
- "我想養一隻貓"
- "我的寵物今天狀態如何？"
- "幫我餵牠"
- "讓牠拍一張照"

## Command reference

### 1) List pets
```bash
bash {baseDir}/scripts/clawpet.sh pets
```

### 2) Adopt a pet
```bash
bash {baseDir}/scripts/clawpet.sh adopt momo
```

### 3) Check current status
```bash
bash {baseDir}/scripts/clawpet.sh status
```

### 4) Interact with pet
```bash
bash {baseDir}/scripts/clawpet.sh interact feed
bash {baseDir}/scripts/clawpet.sh interact play
bash {baseDir}/scripts/clawpet.sh interact rest
```

### 5) Send pet image (RECOMMENDED for image requests)
```bash
bash {baseDir}/scripts/clawpet.sh snapshot
bash {baseDir}/scripts/clawpet.sh snapshot --place "sunny window" --style "soft watercolor"
```
This prints:
- `MEDIA: <image_url>` — public HTTP URL that OpenClaw will auto-send
- `CAPTION: <caption>` — suggested caption text
- `PROMPT: <prompt>` — the full prompt used

With `--json` flag, returns JSON with `image_url`, `caption`, `media.url`.

### 6) Generate text prompt (for advanced use)
```bash
bash {baseDir}/scripts/clawpet.sh prompt
bash {baseDir}/scripts/clawpet.sh prompt --place "sunny window" --style "soft watercolor"
```
Only use this if you need the prompt text to pass to another image generator.

### 7) Auto care
```bash
bash {baseDir}/scripts/clawpet.sh care
bash {baseDir}/scripts/clawpet.sh care --action feed
```

## Agent behavior guidance
1. Always call `bash {baseDir}/scripts/clawpet.sh ...` to avoid missing executable issues.
2. When user says they want a pet, first run `bash {baseDir}/scripts/clawpet.sh pets`, then ask which one they want.
3. For regular check-ins, run `bash {baseDir}/scripts/clawpet.sh status`.
4. For daily care, prefer `bash {baseDir}/scripts/clawpet.sh care`; for explicit requests, run `... interact <action>`.
5. **For image requests, use `snapshot` command (not `prompt`)**. Run `bash {baseDir}/scripts/clawpet.sh snapshot` and it will print `MEDIA: <url>`. This URL is a public HTTP image that Telegram can display directly.
6. Never put local file path into `MEDIA:` (for example `/tmp/...jpg`); always use HTTP(S) URL.
7. If you need explicit send command, use:
   - `openclaw message send --media "<image_url>" --message "<caption>"`
   - or message tool payload `media.url = <image_url>`

## Troubleshooting
- If `clawpet` command is not found, this skill wrapper auto-falls back to:
  - `uvx --from git+https://github.com/yazelin/clawpet.git clawpet ...`
  - `uv tool run --from git+https://github.com/yazelin/clawpet.git clawpet ...`
