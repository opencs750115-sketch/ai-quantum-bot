import json
from datetime import datetime

def update_dashboard_json(bot):
    """
    此函數負責把大腦裡的所有數據，打包並同步給 Streamlit 看板
    """
    # 整理排行格式
    rankings_data = []
    # 假設我們從 bot.sector_matrix 的計算結果拿到排行
    
    # 打包成標準格式
    dashboard_data = {
        "tsec_current": bot.tsec_current if bot.tsec_current else 0.0,
        "active_sector": bot.active_sector if bot.active_sector else "等待 09:05 確立風向",
        "last_update": datetime.now().strftime("%H:%M:%S"),
        "rankings": bot.latest_rankings_list, # 傳入計算好的排行
        "inventory": [
            {
                "股號": k,
                "股名": bot.sector_matrix[bot.active_sector]["name"] if bot.active_sector else "AI股",
                "買進價": v["buy_price"],
                "現價": bot.market_snapshot.get(k, {}).get("current", v["buy_price"]),
                "損益(%)": round(((bot.market_snapshot.get(k, {}).get("current", v["buy_price"]) - v["buy_price"]) / v["buy_price"]) * 100, 2)
            } for k, v in bot.inventory.items()
        ],
        "logs": bot.trade_log[-10:] # 只拿最新的 10 筆日誌，避免手機畫面太長
    }
    
    # 寫入檔案 (GitHub 與 Streamlit 會透過這個檔案即時連動)
    with open("market_state.json", "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=4)
