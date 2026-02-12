# 多物種擴充資料規範（clawpet）

本文件定義如何在不改動核心程式的前提下，新增新的寵物物種。

## 1) 在 `pets/index.json` 註冊

新增一筆條目：

```json
{
  "id": "pet-id",
  "species": "rabbit",
  "file": "pet-id.json",
  "enabled": false
}
```

- `id`：唯一識別字串
- `species`：物種名稱（cat/dog/rabbit/...）
- `file`：對應詳細檔名
- `enabled`：是否在預設清單顯示

## 2) 建立 `pets/<id>.json`

最小欄位如下：

```json
{
  "profile": {
    "name_zh": "中文名",
    "name_en": "EnglishName",
    "species": "rabbit",
    "summary": "一句話介紹"
  },
  "appearance": {
    "breed": "simple breed description",
    "signature": ["feature 1", "feature 2"]
  },
  "personality": {
    "traits": ["trait 1", "trait 2"],
    "favorite_places": ["place 1", "place 2"],
    "voice": "tone"
  },
  "state_defaults": {
    "mood": 70,
    "energy": 70,
    "hunger": 30,
    "bond": 35
  },
  "prompt_snippet": "visual constraints for image prompt"
}
```

## 3) 測試方式

```bash
clawpet pets --all
clawpet show <id>
clawpet adopt <id>
clawpet prompt
```

## 4) 設計原則

- `species` 只做分類，不改互動主流程。
- 狀態欄位固定（mood/energy/hunger/bond），確保技能兼容。
- 角色個性與視覺特徵透過 JSON 驅動，避免硬編碼。

