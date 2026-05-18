"""
pages/1_菜單設計.py — 訓練菜單設計頁

對應計畫書核心功能：
- 人體肌肉圖點選肌群（用 SVG + checkbox 達成）
- 自主設計：肌群 → 推薦動作 → 組合菜單
- AI 協助設計：肌群 + 程度 → AI 產生菜單
"""

import streamlit as st

from database import get_profile, create_menu, list_menus, get_menu_exercises, delete_menu
from exercises_data import MUSCLE_GROUPS, EXERCISES, get_exercises_for_muscles
from ai_menu import generate_menu_with_ai
from muscle_map import render_muscle_map_svg

st.set_page_config(page_title="菜單設計", page_icon="🎯", layout="wide")
st.title("🎯 訓練菜單設計")

profile = get_profile()
if not profile:
    st.warning("請先到首頁完成個人資料設定。")
    st.stop()

# ---- 模式切換 ----
mode = st.radio(
    "設計模式",
    options=["✋ 自主設計", "🤖 AI 協助設計", "📚 已儲存菜單"],
    horizontal=True,
)

st.divider()


# =================================================================
# 共用：肌群選取區（含人體肌肉圖視覺化）
# =================================================================
def muscle_selector(key_prefix: str) -> list[str]:
    col_map, col_check = st.columns([2, 3])

    selected = []
    with col_check:
        st.markdown("**選取要訓練的肌群**")
        muscles = list(MUSCLE_GROUPS.keys())
        cc1, cc2 = st.columns(2)
        for i, m in enumerate(muscles):
            container = cc1 if i < len(muscles) // 2 + len(muscles) % 2 else cc2
            with container:
                if st.checkbox(m, key=f"{key_prefix}_chk_{m}"):
                    selected.append(m)

    with col_map:
        st.markdown("**肌肉圖（紅色 = 已選）**")
        svg = render_muscle_map_svg(selected)
        st.markdown(svg, unsafe_allow_html=True)

    return selected


# =================================================================
# 模式 1：自主設計
# =================================================================
if mode == "✋ 自主設計":
    st.subheader("✋ 自主設計菜單")
    selected_muscles = muscle_selector("self")

    if selected_muscles:
        st.markdown("---")
        st.markdown("**推薦動作** — 勾選想加入菜單的動作：")

        candidates = get_exercises_for_muscles(selected_muscles)
        chosen: list[dict] = []

        for i, ex in enumerate(candidates):
            cols = st.columns([0.5, 2, 2, 1, 1, 3])
            with cols[0]:
                pick = st.checkbox("", key=f"pick_{i}", label_visibility="collapsed")
            with cols[1]:
                st.markdown(f"**{ex['name']}**  \n<small>{ex['muscle_group']}</small>", unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<small>器材：{ex['equipment']}</small>", unsafe_allow_html=True)
            with cols[3]:
                custom_sets = st.number_input("組", min_value=1, max_value=10,
                                              value=ex["sets"], key=f"sets_{i}",
                                              label_visibility="collapsed")
            with cols[4]:
                custom_reps = st.text_input("次", value=ex["reps"], key=f"reps_{i}",
                                            label_visibility="collapsed")
            with cols[5]:
                st.markdown(f"<small>💡 {ex['notes']}</small>", unsafe_allow_html=True)

            if pick:
                chosen.append({
                    "name": ex["name"],
                    "muscle_group": ex["muscle_group"],
                    "equipment": ex["equipment"],
                    "sets": int(custom_sets),
                    "reps": custom_reps,
                    "notes": ex["notes"],
                })

        st.markdown("---")
        if chosen:
            st.success(f"已選 {len(chosen)} 個動作")
            menu_name = st.text_input("菜單名稱", value=f"{' + '.join(selected_muscles)} 訓練日")
            if st.button("💾 儲存菜單", type="primary"):
                menu_id = create_menu(menu_name, selected_muscles, "self", chosen)
                st.success(f"菜單已儲存（ID: {menu_id}）！可到「已儲存菜單」或「訓練紀錄」頁使用。")
        else:
            st.info("請先勾選至少一個動作。")
    else:
        st.info("👆 請先在上方選取至少一個肌群。")


# =================================================================
# 模式 2：AI 協助設計
# =================================================================
elif mode == "🤖 AI 協助設計":
    st.subheader("🤖 AI 協助設計菜單")
    st.caption(f"系統會帶入你的資料：{profile['gender']} · {profile['age']} 歲 · "
               f"{profile['height']} cm · {profile['weight']} kg · {profile['level']}")

    selected_muscles = muscle_selector("ai")

    st.markdown("---")
    c1, c2 = st.columns([1, 2])
    with c1:
        ai_level = st.selectbox(
            "本次菜單程度",
            options=["初學", "中階", "進階"],
            index=["初學", "中階", "進階"].index(profile.get("level", "初學")),
        )
    with c2:
        api_key = st.text_input(
            "OpenAI API Key（選填）",
            type="password",
            help="留空則使用本地規則式菜單；填入則呼叫 GPT 生成。也可改用環境變數 OPENAI_API_KEY。",
        )

    if st.button("✨ 產生菜單", type="primary", disabled=not selected_muscles):
        with st.spinner("生成中..."):
            result = generate_menu_with_ai(profile, selected_muscles, ai_level,
                                           api_key=api_key or None)
            st.session_state["ai_result"] = result
            st.session_state["ai_muscles"] = selected_muscles

    result = st.session_state.get("ai_result")
    if result:
        if "_warning" in result:
            st.warning(result["_warning"])
        if "_source" in result:
            st.caption(f"來源：{result['_source']}")

        st.markdown(f"### 📋 {result.get('menu_name', '訓練菜單')}")
        if result.get("warmup"):
            st.info(f"🔥 熱身：{result['warmup']}")

        for ex in result.get("exercises", []):
            with st.container(border=True):
                cc = st.columns([3, 2, 1, 1, 4])
                cc[0].markdown(f"**{ex['name']}**  \n<small>{ex.get('muscle_group', '')}</small>",
                               unsafe_allow_html=True)
                cc[1].markdown(f"<small>{ex.get('equipment', '')}</small>", unsafe_allow_html=True)
                cc[2].markdown(f"{ex.get('sets', 3)} 組")
                cc[3].markdown(f"{ex.get('reps', '10')} 次")
                cc[4].markdown(f"<small>💡 {ex.get('notes', '')}</small>", unsafe_allow_html=True)

        if result.get("cooldown"):
            st.info(f"🧘 收操：{result['cooldown']}")

        st.markdown("---")
        save_name = st.text_input("儲存為菜單", value=result.get("menu_name", "AI 菜單"))
        if st.button("💾 儲存這份菜單"):
            menu_id = create_menu(
                save_name,
                st.session_state.get("ai_muscles", []),
                "ai",
                result.get("exercises", []),
            )
            st.success(f"已儲存（ID: {menu_id}）")


# =================================================================
# 模式 3：已儲存菜單
# =================================================================
else:
    st.subheader("📚 已儲存菜單")
    menus = list_menus()
    if not menus:
        st.info("還沒有儲存任何菜單，先去設計一份吧！")
    else:
        for m in menus:
            with st.expander(f"📋 {m['name']}　·　{m['source']}　·　{m['created_at']}"):
                exes = get_menu_exercises(m["id"])
                if exes:
                    import pandas as pd
                    df = pd.DataFrame(exes)[["exercise_name", "muscle_group", "equipment",
                                             "target_sets", "target_reps", "notes"]]
                    df.columns = ["動作", "肌群", "器材", "組", "次", "備註"]
                    st.dataframe(df, use_container_width=True, hide_index=True)
                if st.button("🗑️ 刪除", key=f"del_{m['id']}"):
                    delete_menu(m["id"])
                    st.rerun()
