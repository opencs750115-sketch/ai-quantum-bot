import streamlit as st
import pandas as pd
import json
import os

# 設定手機網頁版面
st.set_page_config(page_title="AI 量化輪動監控中心", layout="centered")

st.title("🎯 AI 量化輪動手機監控中心")
st.caption("資金規模：80 萬 | 策略：AI族群開盤動能爆量追價")

DATA_FILE = "market_state.json"

# === 強化防禦：如果檔案不存在，顯示初始待命畫面，絕對不當機 ===
if not os.path.exists(DATA_FILE):
    st.warning("⏳ 雲端大腦正在準備初始化數據，請稍候... (或可於明日 09:00 開盤後查看)")
    
    # 建立一個基礎虛擬資料，讓網頁有東西可以渲染
    state = {
        "tsec_current": 22150.0,
        "active_sector": "等待 09:05 確立風向",
        "last_update": "尚未同步",
        "rankings": [
            {"族群": "AI先進封裝與載板", "動能得分": 0.0, "平均漲幅(%)": 0.0},
            {"族群": "矽光子與光通訊", "動能得分": 0.0, "平均漲幅(%)": 0.0},
            {"族群": "AI周邊與核心零組件", "動能得分": 0.0, "平均漲幅(%)": 0.0}
        ],
        "inventory": [],
        "logs": ["系統初始化中，等待開盤訊號..."]
    }
else:
    # 檔案存在，正常讀取
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        st.error("數據讀取中，請手動重整網頁。")
        st.stop()

# ------------------------------------------------------------------------------
# 區塊一：大盤與當日焦點
# ------------------------------------------------------------------------------
st.subheader("📊 盤中即時狀態")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="加權指數", value=f"{state.get('tsec_current', 0.0):,} 點")
with col2:
    st.metric(label="今日聚焦 AI 族群", value=state.get('active_sector', '未定'))

st.caption(f"最後同步時間：{state.get('last_update', '無')}")
st.markdown("---")

# ------------------------------------------------------------------------------
# 區塊二：族群熱度排行
# ------------------------------------------------------------------------------
st.subheader("🔥 今日 AI 熱錢流向榜")
if "rankings" in state and state["rankings"]:
    df_rank = pd.DataFrame(state["rankings"])
    st.bar_chart(data=df_rank, x="族群", y="動能得分", color="#FF4B4B")
    st.dataframe(df_rank, hide_index=True)
st.markdown("---")

# ------------------------------------------------------------------------------
# 區塊三：即時庫存與賺賠
# ------------------------------------------------------------------------------
st.subheader("💰 模擬持股部位")
if state.get("inventory"):
    df_inv = pd.DataFrame(state["inventory"])
    for idx, row in df_inv.iterrows():
        color = "green" if row.get('損益(%)', 0) > 0 else "red"
        st.markdown(
            f"🍏 **{row.get('股名','AI股')}** | 買進: {row.get('買進價', 0)} → 現價: {row.get('現價', 0)} | "
            f"損益: :{color}[{row.get('損益(%)', 0):+.2f}%]"
        )
else:
    st.info("目前無持股，資金待命中。")
st.markdown("---")

# ------------------------------------------------------------------------------
# 區塊四：即時流水帳日誌
# ------------------------------------------------------------------------------
st.subheader("📜 系統即時日誌")
if "logs" in state:
    for log in reversed(state["logs"]):
        st.text(log)
