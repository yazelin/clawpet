---
name: clawpet
description: "OpenClaw pet companion skill. Manage adopted pets, run interactions, and produce pet image prompts."
metadata:
  openclaw:
    requires:
      bins: [uv]
    install:
      - id: clawpet-pip
        kind: pip
        package: clawpet
        bins: [clawpet]
        label: "Install clawpet (pip install clawpet)"
---

# clawpet — OpenClaw Pet Companion 🐾

Use this skill when the user wants to adopt a pet, check pet status, interact with the pet, or generate a pet image prompt.
Pet status includes passive time-based updates, so each check-in can reflect elapsed time.

## Typical triggers
- "我想養一隻貓"
- "我的寵物今天狀態如何？"
- "幫我餵牠"
- "讓牠拍一張照"

## Command reference

### 1) List pets
```bash
clawpet pets
```

### 2) Adopt a pet
```bash
clawpet adopt momo
```

### 3) Check current status
```bash
clawpet status
```

### 4) Interact with pet
```bash
clawpet interact feed
clawpet interact play
clawpet interact rest
```

### 5) Generate image prompt
```bash
clawpet prompt
clawpet prompt --place "sunny window" --style "soft watercolor"
```

### 6) Auto care
```bash
clawpet care
clawpet care --action feed
```

## Agent behavior guidance
1. When user says they want a pet, first run `clawpet pets`, then ask which one they want.
2. For regular check-ins, run `clawpet status`.
3. For daily care, prefer `clawpet care`; for explicit requests, run `clawpet interact <action>`.
4. For image requests, run `clawpet prompt`, then send/attach the prompt result in your response.
