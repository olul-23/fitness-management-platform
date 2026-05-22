"""
app.py — Streamlit 主程式

對應使用者故事第一步：輸入個人基本資料。
本檔負責：
1. 初始化資料庫
2. 使用者個人資料表單（性別、年齡、身高、體重、健身程度）
3. 系統首頁與導覽說明
"""

import streamlit as st

from database import init_db, save_profile, get_profile

# ---- 頁面設定（必須在第一個 st 呼叫）----
st.set_page_config(
    page_title="健身管理平台",
    page_icon="💪",
    layout="wide",
)

# ---- 啟動時初始化 DB ----
# 若資料表不存在則自動建立
# 避免第一次執行時發生 table not found 錯誤
init_db()


# =================================================================
# 主畫面
# =================================================================

st.title("💪 健身管理平台")
st.caption("從訓練前的菜單設計，到訓練後的紀錄與成果追蹤")

st.divider()

# ---- 左：個人資料表單；右：使用說明 ----
col_form, col_help = st.columns([3, 2])

with col_form:
    st.subheader("📋 個人資料")
    existing = get_profile()

    with st.form("profile_form", clear_on_submit=False):
        gender = st.selectbox(
            "性別",
            options=["男", "女", "不指定"],
            index=["男", "女", "不指定"].index(existing["gender"]) if existing else 0,
        )

        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input(
                "年齡", min_value=10, max_value=100,
                value=existing["age"] if existing else 22, step=1,
            )
            height = st.number_input(
                "身高 (cm)", min_value=100.0, max_value=230.0,
                value=float(existing["height"]) if existing else 170.0, step=0.5,
            )
        with c2:
            weight = st.number_input(
                "體重 (kg)", min_value=30.0, max_value=200.0,
                value=float(existing["weight"]) if existing else 65.0, step=0.5,
            )
            levels = ["初學", "中階", "進階"]
            level = st.selectbox(
                "健身程度",
                options=levels,
                index=levels.index(existing["level"]) if existing and existing["level"] in levels else 0,
                help="影響 AI 菜單生成時的動作數量與強度建議",
            )

        submitted = st.form_submit_button("💾 儲存", type="primary", use_container_width=True)
        if submitted:
            save_profile(gender, int(age), float(height), float(weight), level)
            st.success("個人資料已儲存！")
            st.rerun()

# 顯示 BMI 作為即時健康指標回饋
# 幫助使用者快速了解目前體態區間
    if existing:
        h_m = existing["height"] / 100
        bmi = existing["weight"] / (h_m ** 2)
        st.info(f"BMI：**{bmi:.1f}**　·　最近更新：{existing['updated_at']}")

with col_help:
    st.subheader("📖 使用流程")
    st.markdown(
        """
        1. **📋 個人資料**（本頁）  
           輸入基本資料，供後續 AI 菜單生成參考。
        2. **🎯 菜單設計**  
           點選肌群 → 自主挑選動作，或讓 AI 幫你設計。
        3. **📝 訓練紀錄**  
           依照菜單勾選，或手動新增紀錄。
        4. **📊 成果總結**  
           查看訓練頻率、肌群分布、重量趨勢。
        """
    )
    st.caption("👈 從左側側邊欄切換頁面")
