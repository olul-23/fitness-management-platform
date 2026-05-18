# 健身管理平台

Python 程式設計｜期末專題 · 第 3 組

> 整合「訓練前菜單設計」與「訓練後紀錄管理」的健身管理平台。

---

## 功能對應（計畫書）

| 計畫書項目 | 對應檔案 / 頁面 |
|---|---|
| 個人資料輸入 | `app.py` 首頁 |
| 人體肌肉圖點選 | `muscle_map.py`（SVG）+ `pages/1_🎯_菜單設計.py` |
| 自主設計菜單 | `pages/1_🎯_菜單設計.py`（✋ 自主設計） |
| AI 協助設計菜單 | `pages/1_🎯_菜單設計.py` + `ai_menu.py` |
| 訓練動作資料庫 | `exercises_data.py`（10 大肌群 / 30+ 動作） |
| 依菜單勾選紀錄 | `pages/2_📝_訓練紀錄.py`（Tab 1） |
| 手動新增紀錄 | `pages/2_📝_訓練紀錄.py`（Tab 2） |
| 成果總結（次數/比例/趨勢/完成率） | `pages/3_📊_成果總結.py` |
| 資料儲存 | `database.py`（SQLite） |

---

## 安裝與啟動

```bash
# 1. 建立虛擬環境（建議）
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. 安裝套件
pip install -r requirements.txt

# 3. 啟動
streamlit run app.py
```

預設網址：`http://localhost:8501`

---

## 使用 AI 菜單功能（可選）

AI 菜單模組會優先讀取 `OPENAI_API_KEY` 環境變數，或在頁面上手動輸入。

```bash
export OPENAI_API_KEY="sk-..."     # macOS / Linux
setx OPENAI_API_KEY "sk-..."       # Windows（重開 terminal 才生效）
```

**未設定 key 時系統會自動回退到「本地規則式生成」**，仍可完整展示流程，期末發表零依賴。

---

## 專案結構

```
fitness_platform/
├── app.py                    # Streamlit 主程式 + 個人資料頁
├── database.py               # SQLite 資料表與 CRUD
├── exercises_data.py         # 動作資料庫（肌群 → 動作）
├── ai_menu.py                # OpenAI API 菜單生成（含 fallback）
├── muscle_map.py             # 人體肌肉圖 SVG 視覺化
├── pages/
│   ├── 1_🎯_菜單設計.py
│   ├── 2_📝_訓練紀錄.py
│   └── 3_📊_成果總結.py
├── requirements.txt
└── README.md
```

---

## 資料庫綱要

| 資料表 | 主要欄位 |
|---|---|
| `user_profile` | gender, age, height, weight, level |
| `menus` | name, muscle_groups, source（self/ai） |
| `menu_exercises` | menu_id, exercise_name, muscle_group, equipment, target_sets, target_reps |
| `training_records` | date, exercise_name, sets, reps, weight, menu_id |

SQLite 檔案會自動建在 `fitness_platform/fitness.db`。

---

## 工作分工（對應計畫書）

| 組員 | 主要負責檔案 |
|---|---|
| 黎佩昀 | `exercises_data.py`、`muscle_map.py`、`pages/1_🎯_菜單設計.py` |
| 曾之羽 | `pages/2_📝_訓練紀錄.py`、`pages/3_📊_成果總結.py` |
| 林邵恩 | `app.py`、`database.py`、整體整合與測試 |
| 共同 | `ai_menu.py`（prompt 設計）、`README.md` |

---

## AI 協作說明

依照計畫書「AI 產出初版 → 組員人工檢查修改 → 實際測試確認」原則：

1. **介面程式碼**：Streamlit 元件由 AI 協助生成初版，組員逐頁測試 UX。
2. **動作資料庫**：`exercises_data.py` 內容已參考 ExRx、Bodybuilding.com 等公開來源交叉比對。
3. **AI 菜單 prompt**：見 `ai_menu.py` 的 `_build_prompt()`，要求 JSON 結構化輸出。
4. **Debug**：所有 AI 產出程式碼皆經實際執行測試。

---

## 進階功能（時間允許再做）

計畫書中提到的兩個進階功能，預留位置：

- **多肌群排程邏輯**：可在 `ai_menu.py` 加上「優先順序排序 + 恢復時間檢查」
- **AI 解讀數據**：在 `pages/3_📊_成果總結.py` 加一個按鈕，把彙整後的數據丟給 GPT 產文字建議
