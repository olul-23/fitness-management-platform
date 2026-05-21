"""
pages/3_成果總結.py — 成果總結頁

對應計畫書核心功能：
- 成果總結（次數 / 比例 / 趨勢 / 完成率）
- 資料統計與分析
- 圖表視覺化呈現

負責內容：
- 訓練次數統計
- 肌群訓練比例分析
- 訓練趨勢圖（趨勢 / 完成率）
- 成果總結與視覺化
"""

from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_profile, list_records, list_menus, get_menu_exercises

st.set_page_config(page_title="成果總結", page_icon="📊", layout="wide")
st.title("📊 成果總結")

if not get_profile():
    st.warning("請先到首頁完成個人資料設定。")
    st.stop()

records = list_records()
if not records:
    st.info("還沒有任何訓練紀錄，先去紀錄幾次訓練再回來看看!")
    st.stop()

df = pd.DataFrame(records)
df["date"] = pd.to_datetime(df["date"])

# =================================================================
# 上方 KPI 區
# =================================================================
today = pd.Timestamp(date.today())
week_start = today - pd.Timedelta(days=6)
month_start = today - pd.Timedelta(days=29)

week_count = df[df["date"] >= week_start]["date"].dt.date.nunique()
month_count = df[df["date"] >= month_start]["date"].dt.date.nunique()
total_volume = (df["sets"] * df["reps"] * df["weight"]).sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("📅 本週訓練天數", f"{week_count} 天")
k2.metric("📆 近 30 日訓練天數", f"{month_count} 天")
k3.metric("🔢 累計紀錄筆數", f"{len(df)} 筆")
k4.metric("🏋️ 累計總量 (kg)", f"{total_volume:,.0f}",
          help="總量 = 組數 × 次數 × 重量 的加總，可粗略反映訓練負荷")

st.divider()

# =================================================================
# 圖表區（左：肌群分布；右：訓練頻率）
# =================================================================
c1, c2 = st.columns(2)

with c1:
    st.subheader("💪 肌群訓練分布")
    muscle_stats = df.groupby("muscle_group").size().reset_index(name="次數")
    muscle_stats = muscle_stats[muscle_stats["muscle_group"].astype(bool)]
    if not muscle_stats.empty:
        fig = px.pie(muscle_stats, names="muscle_group", values="次數", hole=0.4)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=True, height=350, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("尚無肌群資料")

with c2:
    st.subheader("📈 訓練頻率（近 30 日）")
    recent = df[df["date"] >= month_start].copy()
    daily = recent.groupby(recent["date"].dt.date).size().reset_index(name="紀錄筆數")
    daily.columns = ["日期", "紀錄筆數"]
    if not daily.empty:
        fig = px.bar(daily, x="日期", y="紀錄筆數")
        fig.update_layout(height=350, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("近 30 日無紀錄")

st.divider()

# =================================================================
# 重量趨勢圖（依動作）
# =================================================================
st.subheader("📊 重量進步趨勢")
st.caption("選一個動作，看每次訓練的最高重量變化")

exercise_options = sorted(df["exercise_name"].unique().tolist())
selected_ex = st.selectbox("選擇動作", options=exercise_options)

ex_df = df[df["exercise_name"] == selected_ex].copy()
trend = ex_df.groupby(ex_df["date"].dt.date).agg(
    最高重量=("weight", "max"),
    平均重量=("weight", "mean"),
).reset_index()
trend.columns = ["日期", "最高重量", "平均重量"]

if len(trend) >= 1:
    fig = px.line(trend, x="日期", y=["最高重量", "平均重量"], markers=True)
    fig.update_layout(height=380, yaxis_title="重量 (kg)", legend_title="")
    st.plotly_chart(fig, use_container_width=True)

    if len(trend) >= 2:
        delta = trend["最高重量"].iloc[-1] - trend["最高重量"].iloc[0]
        sign = "+" if delta >= 0 else ""
        st.success(f"從第一次到最近一次，最高重量變化：**{sign}{delta:.1f} kg**")
else:
    st.info("尚無此動作的紀錄")

st.divider()

# =================================================================
# 訓練完成率（依菜單）
# =================================================================
st.subheader("✅ 菜單完成率")
st.caption("有跟著菜單做的訓練，實際完成了幾項")

menus = list_menus()
completion_rows = []
for m in menus:
    target_exes = get_menu_exercises(m["id"])
    if not target_exes:
        continue
    target_count = len(target_exes)
    done_df = df[df["menu_id"] == m["id"]]
    if done_df.empty:
        continue
    by_day = done_df.groupby(done_df["date"].dt.date)["source_menu_exercise_id"].nunique()
    avg_done = by_day.mean()
    completion_rows.append({
        "菜單": m["name"],
        "目標動作數": target_count,
        "平均完成數": round(avg_done, 1),
        "完成率": f"{(avg_done / target_count * 100):.0f}%",
        "使用次數": len(by_day),
    })

if completion_rows:
    st.dataframe(pd.DataFrame(completion_rows), use_container_width=True, hide_index=True)
else:
    st.info("目前還沒有依菜單訓練的紀錄。手動紀錄不會列入完成率計算。")
