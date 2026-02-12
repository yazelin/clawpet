# clawpet

OpenClaw 寵物陪伴專案（MVP），以貓咪起步並對齊 catime 角色資料概念，後續可擴展多物種。

## 目標
- 把 OpenClaw 互動延伸為「可養的 AI 寵物」體驗。
- 安裝流程維持低摩擦，盡量一條命令上手。
- 技術上對齊 catime 的角色資料設計，方便共用與擴充。

## MVP 功能
- 4 隻預設可養貓咪：Momo、Mochi、Captain、Lingling。
- 寵物狀態管理：mood / energy / hunger / bond。
- 被動狀態演進：依時間自動變化，讓寵物更有「活著」感。
- 互動命令：`feed` / `play` / `rest`。
- 自動照護命令：`clawpet care`（依狀態自動選擇餵食/休息/玩耍）。
- 圖像提示詞生成：`clawpet prompt`。
- 可直接送圖 URL：`clawpet snapshot`（輸出可用於 MEDIA 的 HTTP 圖片網址）。
- catime 輸出解析：`clawpet catime <query>`。
- OpenClaw 本地安裝器：自動安裝 CLI + skill + config + SOUL 注入。

## 文件
- 提案：`docs/proposal.md`
- 執行計劃：`docs/execution-plan.md`
- 多物種資料規範：`docs/multi-species-schema.md`
- 完成報告：`docs/completion-report.md`

## 本地快速安裝（OpenClaw）
```bash
./scripts/install_local.sh
```

## CLI 快速開始
```bash
clawpet pets
clawpet adopt momo
clawpet care
clawpet status
clawpet prompt
clawpet snapshot --json
clawpet catime latest --json
```

## 指令總覽
```bash
clawpet pets [--all] [--json]
clawpet show <pet_id> [--json]
clawpet adopt <pet_id> [--profile <path>] [--json]
clawpet status [--profile <path>] [--json]
clawpet interact <feed|play|rest> [--profile <path>] [--json]
clawpet care [--action <feed|play|rest>] [--profile <path>] [--json]
clawpet prompt [--pet-id <id>] [--place <scene>] [--style <style>] [--json]
clawpet snapshot [--pet-id <id>] [--place <scene>] [--style <style>] [--json]
clawpet catime [query] [--repo owner/repo] [--json]
```

## OpenClaw 使用流程（建議）
1. 執行 `./scripts/install_local.sh`
2. 在 agent 對話中先做角色選擇（對應 `clawpet pets` + `clawpet adopt <id>`）
3. 日常互動使用 `clawpet care` 或 `clawpet interact <action>`
4. 要圖片時優先使用 `clawpet snapshot --json`，直接拿 `image_url` 發送媒體

## ClawHub 安裝（推薦）
```bash
clawhub install clawpet
```

安裝後 skill 會透過 `skill/scripts/clawpet.sh` 自動嘗試：
1. 直接用本機 `clawpet`
2. 若不存在，改用 `uvx --from git+https://github.com/yazelin/clawpet.git clawpet ...`
3. 再退回 `uv tool run --from git+https://github.com/yazelin/clawpet.git clawpet ...`

若你先前遇到「沒有可執行文件」，請執行：
```bash
clawhub update clawpet
```

若你遇到「只顯示路徑，沒有插圖」，請確認：
- 使用 `snapshot` 的 `image_url`（HTTP/HTTPS），不要送 `/tmp/...` 這類本機路徑
- 更新到最新版：`clawhub update clawpet`

## 開發分支紀錄（已完成）
- `docs/proposal-plan`
- `docs/execution-plan`
- `feat/core-pet-engine`
- `feat/openclaw-skill-installer`
- `feat/catime-compat-and-multi-species-ready`
- `chore/readme-and-validation`
- `feat/pet-lifecycle`
- `docs/final-report`

## 開發與測試
```bash
uv sync --extra dev
uv run pytest -q
```
