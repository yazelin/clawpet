# OpenClaw 寵物專案執行計劃書（MVP）

> 本計劃依「先提案、再落地」原則，採分支逐步實作與可驗收交付。

## 1) 實作總策略

- **技術主軸**：Python CLI + OpenClaw Skill + 自動安裝腳本。
- **相容主軸**：資料格式與角色觀念盡量對齊 catime（四貓起步、可擴展）。
- **體驗主軸**：先完成「最少步驟可玩」，再逐步擴充玩法深度。

---

## 2) 分支規劃與實作順序

### Branch A — `feat/core-pet-engine`
**目標**：完成可運行的寵物核心與 CLI。

**內容**
- 建立 Python 套件骨架（`pyproject.toml`, `src/`, `tests/`）
- 建立寵物資料模型與載入器（JSON）
- 導入 4 隻貓角色（與 catime 角色命名相容）
- CLI 功能：
  - `pets`：列出可養寵物
  - `show <pet_id>`：顯示個體資料
  - `adopt <pet_id>`：設定當前寵物
  - `status`：顯示目前寵物狀態
  - `interact`：餵食/玩耍/休息，更新狀態
  - `prompt`：輸出可給圖像生成的場景提示

**驗收標準**
- CLI 可安裝、可執行、無崩潰
- 狀態可被更新並持久化於本地檔案
- 單元測試可通過

---

### Branch B — `feat/openclaw-skill-installer`
**目標**：完成 OpenClaw 可直接接入能力。

**內容**
- 新增 `skill/SKILL.md`（含 openclaw install metadata）
- 新增 `templates/soul-injection.md`
- 新增 `scripts/install_local.sh`
  - 安裝 Python 套件
  - 複製 skill 至 `~/.openclaw/skills/`
  - 合併 `openclaw.json` 設定
  - 注入 SOUL 段落（避免重複注入）

**驗收標準**
- 一條命令可完成本地安裝
- 安裝後 `openclaw.json` 包含 skill 設定
- SOUL 注入成功且可重複執行

---

### Branch C — `feat/catime-compat-and-multi-species-ready`
**目標**：做出 catime 相容介面 + 多物種可擴充準備。

**內容**
- 新增 catime 輸出解析（latest/query）
- CLI 增加 `catime` 子命令（若安裝 catime）
- 在資料模型中正式納入 `species` 與共用 traits 欄位
- 新增「新增新物種」文件化規範

**驗收標準**
- 可正確解析 catime CLI 的 URL 與基本 metadata
- 不改核心程式也能新增新寵物資料檔

---

### Branch D — `chore/readme-and-validation`
**目標**：完成可交付文件與最終驗證。

**內容**
- 補齊 README（快速安裝、快速開始、指令表）
- 補齊測試案例
- 執行測試與基本流程驗證
- 整理 MVP 完成報告

**驗收標準**
- 新使用者可依 README 在短時間內完成安裝與操作
- 測試綠燈

---

## 3) 資料結構規範（MVP）

### `pets/index.json`
- 包含版本、預設寵物、角色列表
- 每個角色具備：
  - `id`
  - `species`
  - `file`
  - `enabled`

### `pets/<id>.json`
- `profile`：名稱/物種/外觀
- `personality`：性格/語氣/偏好
- `state_defaults`：初始狀態
- `prompt_snippet`：圖像提示片段

---

## 4) 風險控管

- **安裝腳本覆寫風險**：採合併策略，不整檔覆寫 `openclaw.json`
- **跨平台腳本差異**：以 POSIX shell + Python JSON merge 避免依賴 jq
- **外部 CLI 依賴不在場**：catime 功能採「可選啟用」與清楚錯誤訊息

---

## 5) 完成定義（Definition of Done）

以下全部滿足才算 MVP 完成：
1. 提案與執行計劃文件齊全
2. 分支 A/B/C/D 全部完成並合併回 main
3. CLI 可安裝執行，測試通過
4. OpenClaw skill 本地安裝成功
5. 至少 4 隻貓可被選擇與互動
6. 保留未來多物種擴充能力
