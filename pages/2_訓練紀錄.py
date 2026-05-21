"""
pages/2_訓練紀錄.py — 訓練紀錄頁

對應計畫書核心功能：
- 從既有菜單勾選完成項目（並填入實際組數 / 次數 / 重量）
- 手動新增訓練紀錄
- 歷史紀錄表格、刪除功能
- 訓練紀錄管理

負責內容：
- 訓練項目紀錄
- 重量與次數輸入
- 訓練日期管理
- 訓練資料儲存
"""

from datetime import date

import pandas as pd
import streamlit as st

from database import (
    get_profile, list_menus, get_menu_exercises,
    add_record, list_records, delete_record,
)
from exercises_data import get_all_exercise_names, find_muscle_group, MUSCLE_GROUPS

st.set_page_config(page_title="訓練紀錄", page_icon="📝", layout="wide")
st.title("📝 訓練紀錄")

if not get_profile():
    st.warning("請先到首頁完成個人資料設定。")
    st.stop()

tab1, tab2, tab3 = st.tabs(["✅ 依菜單勾選", "✏️ 手動新增", "📜 歷史紀錄"])


# =================================================================
# Tab 1：依菜單勾選
# =================================================================
with tab1:
    menus = list_menus()
    if not menus:
        st.info("還沒有儲存任何菜單，先到「菜單設計」頁建立一份。")
    else:
        menu_options = {f"{m['name']}（{m['created_at'][:10]}）": m["id"] for m in menus}
        picked = st.selectbox("選擇要紀錄的菜單", options=list(menu_options.keys()))
        menu_id = menu_options[picked]

        train_date = st.date_input("訓練日期", value=date.today(), key="menu_date")

        exes = get_menu_exercises(menu_id)
        st.caption(f"共 {len(exes)} 個動作，勾選並填入實際數據後送出。")

        st.markdown("---")
        with st.form("menu_record_form"):
            entries = []
            for ex in exes:
                cols = st.columns([0.4, 2, 1, 1, 1, 1])
                with cols[0]:
                    done = st.checkbox("", key=f"done_{ex['id']}", label_visibility="collapsed")
                with cols[1]:
                    st.markdown(f"**{ex['exercise_name']}**  \n"
                                f"<small>{ex['muscle_group']} · 目標：{ex['target_sets']} 組 × {ex['target_reps']}</small>",
                                unsafe_allow_html=True)
                with cols[2]:
                    actual_sets = st.number_input(
                        "組數", min_value=1, max_value=20,
                        value=int(ex["target_sets"]),
                        key=f"as_{ex['id']}", label_visibility="collapsed",
                    )
                with cols[3]:
                    actual_reps = st.number_input(
                        "次數/組", min_value=1, max_value=100,
                        value=10, key=f"ar_{ex['id']}", label_visibility="collapsed",
                    )
                with cols[4]:
                    weight = st.number_input(
                        "重量(kg)", min_value=0.0, max_value=500.0,
                        value=0.0, step=2.5,
                        key=f"aw_{ex['id']}", label_visibility="collapsed",
                    )
                with cols[5]:
                    note = st.text_input(
                        "備註", value="", key=f"an_{ex['id']}",
                        label_visibility="collapsed", placeholder="備註",
                    )

                entries.append({
                    "done": done,
                    "menu_exercise_id": ex["id"],
                    "name": ex["exercise_name"],
                    "muscle_group": ex["muscle_group"],
                    "sets": int(actual_sets),
                    "reps": int(actual_reps),
                    "weight": float(weight),
                    "note": note,
                })

            if st.form_submit_button("💾 送出已勾選紀錄", type="primary"):
                count = 0
                for e in entries:
                    if e["done"]:
                        add_record(
                            date=str(train_date),
                            exercise_name=e["name"],
                            muscle_group=e["muscle_group"],
                            sets=e["sets"], reps=e["reps"], weight=e["weight"],
                            menu_id=menu_id,
                            source_menu_exercise_id=e["menu_exercise_id"],
                            notes=e["note"],
                        )
                        count += 1
                if count:
                    st.success(f"已新增 {count} 筆紀錄！")
                else:
                    st.warning("沒有勾選任何項目。")


# =================================================================
# Tab 2：手動新增
# =================================================================
with tab2:
    st.caption("照菜單之外的訓練，或自由訓練都可用此頁紀錄。")
    with st.form("manual_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            m_date = st.date_input("日期", value=date.today(), key="manual_date")
            preset_names = get_all_exercise_names()
            use_preset = st.checkbox("從動作庫挑選", value=True)
            if use_preset:
                m_name = st.selectbox("動作名稱", options=preset_names)
                m_muscle = find_muscle_group(m_name)
                st.caption(f"自動帶入肌群：{m_muscle or '（未對應）'}")
            else:
                m_name = st.text_input("動作名稱")
                m_muscle = st.selectbox("肌群", options=list(MUSCLE_GROUPS.keys()))
        with c2:
            m_sets = st.number_input("組數", min_value=1, max_value=20, value=3)
            m_reps = st.number_input("次數/組", min_value=1, max_value=100, value=10)
            m_weight = st.number_input("重量 (kg)", min_value=0.0, max_value=500.0,
                                       value=20.0, step=2.5)
            m_note = st.text_input("備註", value="")

        if st.form_submit_button("💾 新增紀錄", type="primary"):
            if m_name:
                add_record(
                    date=str(m_date),
                    exercise_name=m_name,
                    muscle_group=m_muscle,
                    sets=int(m_sets), reps=int(m_reps), weight=float(m_weight),
                    notes=m_note,
                )
                st.success("已新增！")
            else:
                st.error("請輸入動作名稱")


# =================================================================
# Tab 3：歷史紀錄
# =================================================================
with tab3:
    records = list_records()
    if not records:
        st.info("還沒有任何訓練紀錄。")
    else:
        df = pd.DataFrame(records)
        st.caption(f"共 {len(df)} 筆紀錄")

        muscles_in_records = sorted(set(df["muscle_group"].dropna().tolist()))
        filt = st.multiselect("依肌群篩選", options=muscles_in_records)
        view = df if not filt else df[df["muscle_group"].isin(filt)]

        show = view[["date", "exercise_name", "muscle_group", "sets", "reps", "weight", "notes"]].copy()
        show.columns = ["日期", "動作", "肌群", "組", "次/組", "重量(kg)", "備註"]
        st.dataframe(show, use_container_width=True, hide_index=True)

        st.markdown("---")
        with st.expander("🗑️ 刪除紀錄"):
            del_id = st.number_input("輸入要刪除的紀錄 ID", min_value=1, step=1)
            st.caption("ID 可在資料庫中查到，或匯出 CSV 後查看。建議只在輸入錯誤時使用。")
            if st.button("確認刪除"):
                delete_record(int(del_id))
                st.success(f"已刪除紀錄 {del_id}")
                st.rerun()
