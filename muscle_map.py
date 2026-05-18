"""
muscle_map.py — 人體肌肉圖視覺化元件

對應計畫書「人體肌肉圖點選介面」核心功能。
產生 SVG 字串：使用者選了哪些肌群就把對應區塊塗色，
搭配 Streamlit 的 checkbox 完成「點選 → 視覺回饋」互動。

之所以用 SVG + checkbox 而不是真的可點擊圖：
- Streamlit 對 SVG 原生點擊事件支援有限
- checkbox 配合 SVG 視覺化是最穩定、跨環境都能跑的方案
- 期末展示時組員只要不出 bug，視覺效果一樣達成
"""

# 各肌群在 SVG 中的多邊形/橢圓座標
# 圖採前後兩個人體側影並排
MUSCLE_REGIONS = {
    # === 正面 ===
    "胸": [("ellipse", 90, 130, 22, 14), ("ellipse", 130, 130, 22, 14)],
    "肩": [("ellipse", 70, 110, 14, 12), ("ellipse", 150, 110, 14, 12)],
    "二頭": [("ellipse", 58, 145, 10, 18), ("ellipse", 162, 145, 10, 18)],
    "核心": [("rect", 95, 150, 30, 50)],
    "腿前側（股四頭）": [("rect", 88, 220, 18, 60), ("rect", 114, 220, 18, 60)],
    # === 背面 ===
    "背": [("rect", 270, 115, 60, 50)],
    "三頭": [("ellipse", 252, 145, 10, 18), ("ellipse", 348, 145, 10, 18)],
    "臀": [("ellipse", 285, 215, 18, 14), ("ellipse", 315, 215, 18, 14)],
    "腿後側（腿後腱）": [("rect", 278, 230, 18, 50), ("rect", 304, 230, 18, 50)],
    "小腿": [("rect", 280, 295, 14, 35), ("rect", 306, 295, 14, 35)],
}

SELECTED_FILL = "#e74c3c"   # 紅色 — 選取
DEFAULT_FILL = "#bdc3c7"    # 灰色 — 未選
OUTLINE = "#2c3e50"


def _body_outline() -> str:
    """簡化人體側影：頭、軀幹、雙臂、雙腿（前後兩個）。"""
    parts = []
    # 正面
    parts.append('<circle cx="110" cy="60" r="22" fill="#ecf0f1" stroke="#2c3e50" stroke-width="1.5"/>')
    parts.append('<path d="M 80,90 L 140,90 L 145,200 L 130,205 L 130,330 L 115,335 L 105,335 L 90,330 L 90,205 L 75,200 Z" fill="#ecf0f1" stroke="#2c3e50" stroke-width="1.5"/>')
    parts.append('<path d="M 60,100 L 78,105 L 75,175 L 60,180 Z" fill="#ecf0f1" stroke="#2c3e50" stroke-width="1.5"/>')
    parts.append('<path d="M 160,100 L 142,105 L 145,175 L 160,180 Z" fill="#ecf0f1" stroke="#2c3e50" stroke-width="1.5"/>')
    parts.append('<text x="110" y="355" text-anchor="middle" font-size="12" fill="#2c3e50" font-weight="bold">正面</text>')
    # 背面
    parts.append('<circle cx="300" cy="60" r="22" fill="#ecf0f1" stroke="#2c3e50" stroke-width="1.5"/>')
    parts.append('<path d="M 270,90 L 330,90 L 335,200 L 320,205 L 320,330 L 305,335 L 295,335 L 280,330 L 280,205 L 265,200 Z" fill="#ecf0f1" stroke="#2c3e50" stroke-width="1.5"/>')
    parts.append('<path d="M 250,100 L 268,105 L 265,175 L 250,180 Z" fill="#ecf0f1" stroke="#2c3e50" stroke-width="1.5"/>')
    parts.append('<path d="M 350,100 L 332,105 L 335,175 L 350,180 Z" fill="#ecf0f1" stroke="#2c3e50" stroke-width="1.5"/>')
    parts.append('<text x="300" y="355" text-anchor="middle" font-size="12" fill="#2c3e50" font-weight="bold">背面</text>')
    return "\n".join(parts)


def _shape_svg(shape: tuple, fill: str) -> str:
    kind = shape[0]
    if kind == "ellipse":
        _, cx, cy, rx, ry = shape
        return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{OUTLINE}" stroke-width="1" opacity="0.85"/>'
    elif kind == "rect":
        _, x, y, w, h = shape
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{OUTLINE}" stroke-width="1" opacity="0.85"/>'
    return ""


def render_muscle_map_svg(selected_muscles: list[str]) -> str:
    """
    回傳完整 SVG 字串。
    selected_muscles 中的肌群會塗紅色，其餘灰色。
    """
    shapes = []
    for muscle, regions in MUSCLE_REGIONS.items():
        fill = SELECTED_FILL if muscle in selected_muscles else DEFAULT_FILL
        for region in regions:
            shapes.append(_shape_svg(region, fill))

    svg = f"""
    <svg viewBox="0 0 410 370" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;height:auto;background:#ffffff;border-radius:8px;">
      {_body_outline()}
      {''.join(shapes)}
    </svg>
    """
    return svg
