# clawpet

OpenClaw 寵物陪伴專案（MVP），以貓咪起步並對齊 catime 角色資料概念，後續可擴展多物種。

## 目標
- 把 OpenClaw 互動延伸為「可養的 AI 寵物」體驗。
- 安裝流程維持低摩擦，盡量一條命令上手。
- 技術上對齊 catime 的角色資料設計，方便共用與擴充。

## MVP 功能
- 4 隻預設可養貓咪：Momo、Mochi、Captain、Lingling。
- 寵物狀態管理：mood / energy / hunger / bond。
- 互動命令：`feed` / `play` / `rest`。
- 圖像提示詞生成：`clawpet prompt`。
- catime 輸出解析：`clawpet catime <query>`。
- OpenClaw 本地安裝器：自動安裝 CLI + skill + config + SOUL 注入。

## 文件
- 提案：`docs/proposal.md`
- 執行計劃：`docs/execution-plan.md`
- 多物種資料規範：`docs/multi-species-schema.md`

## 本地快速安裝（OpenClaw）
```bash
./scripts/install_local.sh
```

## CLI 快速開始
```bash
clawpet pets
clawpet adopt momo
clawpet interact play
clawpet prompt
clawpet catime latest --json
```

## 指令總覽
```bash
clawpet pets [--all] [--json]
clawpet show <pet_id> [--json]
clawpet adopt <pet_id> [--profile <path>] [--json]
clawpet status [--profile <path>] [--json]
clawpet interact <feed|play|rest> [--profile <path>] [--json]
clawpet prompt [--pet-id <id>] [--place <scene>] [--style <style>] [--json]
clawpet catime [query] [--repo owner/repo] [--json]
```

## 開發與測試
```bash
uv sync --extra dev
uv run pytest -q
```
