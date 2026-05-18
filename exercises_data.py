"""
exercises_data.py — 動作資料庫

對應計畫書「訓練動作資料庫建立」項目。
以肌群為 key，列出常見動作、器材、建議組數/次數。
資料整理自公開健身教學資源（如 ExRx、Bodybuilding.com 等），實際應用前已交叉比對。
"""

# 肌群顯示名（中文）與內部 key 對應
MUSCLE_GROUPS = {
    "胸": "chest",
    "背": "back",
    "肩": "shoulders",
    "二頭": "biceps",
    "三頭": "triceps",
    "腿前側（股四頭）": "quads",
    "腿後側（腿後腱）": "hamstrings",
    "臀": "glutes",
    "小腿": "calves",
    "核心": "core",
}

# 每個肌群對應的動作清單
EXERCISES: dict[str, list[dict]] = {
    "胸": [
        {"name": "槓鈴臥推", "equipment": "槓鈴 + 臥推椅", "sets": 4, "reps": "8-12",
         "notes": "胸大肌複合動作，新手建議從空槓練起"},
        {"name": "啞鈴臥推", "equipment": "啞鈴 + 臥推椅", "sets": 3, "reps": "10-12",
         "notes": "活動範圍較大，可加強肌肉控制"},
        {"name": "上斜啞鈴臥推", "equipment": "啞鈴 + 上斜椅", "sets": 3, "reps": "10-12",
         "notes": "強化上胸"},
        {"name": "雙槓撐體", "equipment": "雙槓架", "sets": 3, "reps": "8-12",
         "notes": "身體前傾偏胸，直立偏三頭"},
        {"name": "啞鈴飛鳥", "equipment": "啞鈴 + 臥推椅", "sets": 3, "reps": "12-15",
         "notes": "孤立胸肌，重量勿過大"},
    ],
    "背": [
        {"name": "引體向上", "equipment": "單槓", "sets": 4, "reps": "8-12",
         "notes": "背闊肌王牌動作，新手可用彈力帶輔助"},
        {"name": "槓鈴划船", "equipment": "槓鈴", "sets": 4, "reps": "8-12",
         "notes": "上半身與地面約 45 度，保持腰背中立"},
        {"name": "滑輪下拉", "equipment": "滑輪機", "sets": 3, "reps": "10-12",
         "notes": "適合無法做引體向上的新手"},
        {"name": "坐姿划船", "equipment": "坐姿划船機", "sets": 3, "reps": "10-12",
         "notes": "強化中背與菱形肌"},
        {"name": "硬舉", "equipment": "槓鈴", "sets": 3, "reps": "5-8",
         "notes": "全身複合動作，新手務必先學技術"},
    ],
    "肩": [
        {"name": "啞鈴肩推", "equipment": "啞鈴 + 臥推椅", "sets": 4, "reps": "8-12",
         "notes": "肩部複合主動作"},
        {"name": "槓鈴肩推", "equipment": "槓鈴", "sets": 3, "reps": "8-10",
         "notes": "可選站姿或坐姿"},
        {"name": "啞鈴側平舉", "equipment": "啞鈴", "sets": 3, "reps": "12-15",
         "notes": "孤立中三角肌，重量輕、控制慢"},
        {"name": "面拉", "equipment": "繩索機 + 繩索", "sets": 3, "reps": "12-15",
         "notes": "後三角肌與肩部健康，建議高頻"},
        {"name": "啞鈴前平舉", "equipment": "啞鈴", "sets": 3, "reps": "12-15",
         "notes": "強化前三角肌"},
    ],
    "二頭": [
        {"name": "槓鈴彎舉", "equipment": "槓鈴", "sets": 3, "reps": "8-12",
         "notes": "二頭肌標準主動作"},
        {"name": "啞鈴錘式彎舉", "equipment": "啞鈴", "sets": 3, "reps": "10-12",
         "notes": "兼顧二頭與肱橈肌"},
        {"name": "斜板彎舉", "equipment": "啞鈴 + 上斜椅", "sets": 3, "reps": "10-12",
         "notes": "拉長二頭起始位置，刺激更深"},
    ],
    "三頭": [
        {"name": "窄握臥推", "equipment": "槓鈴 + 臥推椅", "sets": 3, "reps": "8-12",
         "notes": "三頭肌複合動作"},
        {"name": "繩索下壓", "equipment": "繩索機 + 繩索", "sets": 3, "reps": "10-12",
         "notes": "孤立三頭，肘部固定"},
        {"name": "頭頂三頭伸展", "equipment": "啞鈴", "sets": 3, "reps": "10-12",
         "notes": "拉長三頭長頭"},
    ],
    "腿前側（股四頭）": [
        {"name": "槓鈴深蹲", "equipment": "槓鈴 + 蹲舉架", "sets": 4, "reps": "6-10",
         "notes": "下肢王牌動作，務必學好姿勢"},
        {"name": "腿推", "equipment": "腿推機", "sets": 4, "reps": "10-12",
         "notes": "對下背壓力較小，適合新手"},
        {"name": "腿伸展", "equipment": "腿伸展機", "sets": 3, "reps": "12-15",
         "notes": "孤立股四頭"},
        {"name": "保加利亞分腿蹲", "equipment": "啞鈴 + 椅子", "sets": 3, "reps": "10-12",
         "notes": "單腿訓練，改善左右肌力失衡"},
    ],
    "腿後側（腿後腱）": [
        {"name": "羅馬尼亞硬舉", "equipment": "槓鈴", "sets": 4, "reps": "8-12",
         "notes": "腿後肌主動作，膝微彎、髖主導"},
        {"name": "俯臥腿彎舉", "equipment": "腿彎舉機", "sets": 3, "reps": "10-12",
         "notes": "孤立腿後腱"},
        {"name": "早安式", "equipment": "槓鈴", "sets": 3, "reps": "10-12",
         "notes": "下背 + 腿後，新手重量保守"},
    ],
    "臀": [
        {"name": "臀推", "equipment": "槓鈴 + 臥推椅", "sets": 4, "reps": "8-12",
         "notes": "臀肌孤立主動作"},
        {"name": "相撲硬舉", "equipment": "槓鈴", "sets": 3, "reps": "8-10",
         "notes": "寬站姿，臀部參與度高"},
        {"name": "髖外展機", "equipment": "髖外展機", "sets": 3, "reps": "12-15",
         "notes": "刺激臀中肌"},
    ],
    "小腿": [
        {"name": "站姿提踵", "equipment": "提踵機（或啞鈴）", "sets": 4, "reps": "12-15",
         "notes": "腓腸肌為主"},
        {"name": "坐姿提踵", "equipment": "坐姿提踵機", "sets": 3, "reps": "15-20",
         "notes": "比目魚肌為主"},
    ],
    "核心": [
        {"name": "棒式", "equipment": "徒手", "sets": 3, "reps": "30-60秒",
         "notes": "核心穩定基礎"},
        {"name": "懸吊抬腿", "equipment": "單槓", "sets": 3, "reps": "10-15",
         "notes": "下腹強化"},
        {"name": "腹輪", "equipment": "腹輪", "sets": 3, "reps": "8-12",
         "notes": "進階核心動作"},
        {"name": "俄羅斯轉體", "equipment": "啞鈴或槓片", "sets": 3, "reps": "20（每側10）",
         "notes": "腹斜肌"},
    ],
}


def get_exercises_for_muscles(muscle_groups: list[str]) -> list[dict]:
    """給定肌群清單，回傳所有對應動作（含 muscle_group 欄位）。"""
    result = []
    for muscle in muscle_groups:
        for ex in EXERCISES.get(muscle, []):
            item = dict(ex)
            item["muscle_group"] = muscle
            result.append(item)
    return result


def get_all_exercise_names() -> list[str]:
    """取得所有動作名稱（用於手動紀錄時的下拉選單）。"""
    names = []
    for ex_list in EXERCISES.values():
        for ex in ex_list:
            names.append(ex["name"])
    return sorted(set(names))


def find_muscle_group(exercise_name: str) -> str:
    """反查動作對應的肌群。"""
    for muscle, ex_list in EXERCISES.items():
        for ex in ex_list:
            if ex["name"] == exercise_name:
                return muscle
    return ""
