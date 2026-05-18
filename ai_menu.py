"""
ai_menu.py — AI 協助設計菜單模組

對應計畫書「AI 菜單生成的提示詞設計」。
呼叫 OpenAI API，根據使用者身體資料 + 選取肌群 + 健身程度，
回傳結構化菜單（JSON）。

設計重點：
1. 強制要求 JSON 輸出，方便程式解析（response_format=json_object）
2. Prompt 內嵌使用者基本資料，產出客製化內容
3. 若 API 失敗或未設定 key，回退到本地規則式生成，確保展示流程不中斷
"""

import json
import os
from typing import Optional

from exercises_data import EXERCISES, get_exercises_for_muscles


def _build_prompt(profile: dict, muscle_groups: list[str], level: str) -> str:
    """組合送給 LLM 的 prompt。"""
    available = {m: [e["name"] for e in EXERCISES.get(m, [])] for m in muscle_groups}
    return f"""你是一位專業健身教練。請為以下使用者設計一份單日訓練菜單。

使用者資料：
- 性別：{profile.get('gender', '未提供')}
- 年齡：{profile.get('age', '未提供')} 歲
- 身高：{profile.get('height', '未提供')} cm
- 體重：{profile.get('weight', '未提供')} kg
- 健身程度：{level}

訓練肌群：{', '.join(muscle_groups)}

可選動作（請優先從中挑選，必要時可加入其他常見動作）：
{json.dumps(available, ensure_ascii=False, indent=2)}

設計原則：
- 初學者：3-4 個動作，著重複合動作，組數較少
- 中階：4-6 個動作，複合 + 孤立搭配
- 進階：5-7 個動作，安排合理的訓練順序（大肌群先、小肌群後）

請務必只回傳合法 JSON，格式如下：
{{
  "menu_name": "菜單名稱（簡短）",
  "warmup": "熱身建議（一句話）",
  "exercises": [
    {{
      "name": "動作名稱",
      "muscle_group": "對應肌群",
      "equipment": "所需器材",
      "sets": 4,
      "reps": "8-12",
      "notes": "技術提醒（一句話）"
    }}
  ],
  "cooldown": "收操建議（一句話）"
}}
"""


def generate_menu_with_ai(profile: dict, muscle_groups: list[str], level: str,
                          api_key: Optional[str] = None) -> dict:
    """
    呼叫 OpenAI API 生成菜單。
    若 api_key 為 None 或呼叫失敗，回退到 fallback_menu()。
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback_menu(muscle_groups, level)

    try:
        # 延後 import，未安裝 openai 套件時不會在啟動時報錯
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = _build_prompt(profile, muscle_groups, level)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是專業健身教練，回覆務必為合法 JSON。"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        content = resp.choices[0].message.content
        data = json.loads(content)
        # 確保 sets 為 int
        for ex in data.get("exercises", []):
            try:
                ex["sets"] = int(ex.get("sets", 3))
            except (ValueError, TypeError):
                ex["sets"] = 3
        return data
    except Exception as e:
        # 任何錯誤都退回本地版本，並把錯誤訊息帶上去供 debug
        result = fallback_menu(muscle_groups, level)
        result["_warning"] = f"AI 生成失敗，已使用本地規則式菜單。原因：{e}"
        return result


def fallback_menu(muscle_groups: list[str], level: str) -> dict:
    """
    無 API key 或 API 失敗時的備援菜單（規則式）。
    依程度從動作庫挑選對應數量。
    """
    per_muscle = {"初學": 2, "中階": 3, "進階": 3}.get(level, 2)
    sets_default = {"初學": 3, "中階": 4, "進階": 4}.get(level, 3)

    exercises = []
    for muscle in muscle_groups:
        pool = EXERCISES.get(muscle, [])
        for ex in pool[:per_muscle]:
            exercises.append({
                "name": ex["name"],
                "muscle_group": muscle,
                "equipment": ex["equipment"],
                "sets": sets_default,
                "reps": ex["reps"],
                "notes": ex["notes"],
            })

    return {
        "menu_name": f"{level} · {' + '.join(muscle_groups)} 訓練日",
        "warmup": "動態伸展 5-10 分鐘，目標肌群輕重量暖身一組。",
        "exercises": exercises,
        "cooldown": "靜態伸展 5-10 分鐘，補充水分與蛋白質。",
        "_source": "本地規則式（未呼叫 AI）",
    }
