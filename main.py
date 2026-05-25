import datetime
import json
import time
import pandas as pd
import requests


# ==============================================================================
# 交易系統大腦與風控核心
# ==============================================================================
class AIQuantumTradingSystem:

    def __init__(self):
        # 資金與風控設定
        self.cash = 800000  # 總資金 80 萬
        self.max_budget_per_stock = 150000  # 單檔現股一張最高預算 15 萬
        self.inventory = {}  # 庫存
        self.trade_log = [
            "09:00:01 【系統】初始化成功，可用資金 800,000 元"
        ]

        # 核心監控多軌矩陣 (高流量、百元上下、純AI電子鏈)
        self.sector_matrix = {
            "AI先進封裝與載板": {
                "main": "3189",
                "name": "景碩",
                "avg_vol": 12000,
                "buddies": ["3037", "6515"],
            },
            "矽光子與光通訊": {
                "main": "3163",
                "name": "波若威",
                "avg_vol": 15000,
                "buddies": ["6442", "2345"],
            },
            "AI周邊與核心零組件": {
                "main": "3013",
                "name": "晟銘電",
                "avg_vol": 35000,
                "buddies": ["2368", "2408"],
            },
        }

        # 盤中動態變數
        self.active_sector = None
        self.tsec_open = None
        self.tsec_current = None
        self.tsec_history = []
        self.latest_rankings_list = []

        # 儲存所有股票的盤中動態
        self.market_snapshot = {}
        for k, v in self.sector_matrix.items():
            all_m = [v["main"]] + v["buddies"]
            for m in all_m:
                self.market_snapshot[m] = {
                    "open": None,
                    "current": None,
                    "volume": 0,
                }

    def is_tsec_healthy(self):
        if self.tsec_current is None or self.tsec_open is None:
            return False
        if self.tsec_current < self.tsec_open:
            return False
        if len(self.tsec_history) > 3:
            past_price = self.tsec_history[-3][1]
            if (past_price - self.tsec_current) / past_price >= 0.0015:
                return False
        return True

    def run_sector_rotation_analysis(self):
        sector_scores = []
        for sector_name, info in self.sector_matrix.items():
            all_members = [info["main"]] + info["buddies"]
            total_return = 0
            up_count = 0
            valid_count = 0

            for m in all_members:
                snap = self.market_snapshot.get(m, {})
                if snap.get("open") and snap.get("current"):
                    ret = (snap["current"] - snap["open"]) / snap["open"]
                    total_return += ret
                    valid_count += 1
                    if ret > 0:
                        up_count += 1

            if valid_count > 0:
                avg_ret = total_return / valid_count
                up_ratio = up_count / valid_count
                score = avg_ret * 0.7 + up_ratio * 0.3
                sector_scores.append(
                    {"sector": sector_name, "score": score, "avg_ret": avg_ret}
                )

        if not sector_scores:
            return

        df_rank = pd.DataFrame(sector_scores).sort_values(
            by="score", ascending=False
        )
        self.active_sector = df_rank.iloc[0]["sector"]

        self.latest_rankings_list = []
        for idx, row in df_rank.reset_index(drop=True).iterrows():
            self.latest_rankings_list.append({
                "族群": row["sector"],
                "動能得分": round(float(row["score"]) * 1000, 1),
                "平均漲幅(%)": round(float(row["avg_ret"]) * 100, 2),
            })

        self.trade_log.append(
            f"09:05:00 【輪動】強勢族群確認：[{self.active_sector}]"
        )

    def execute_trading_logic(self, stock_no, current_time):
        snap = self.market_snapshot.get(stock_no, {})
        current_price = snap.get("current")
        if not current_price:
            return

        # A. 持有庫存的出場檢查
        if stock_no in self.inventory:
            position = self.inventory[stock_no]
            if current_price > position["max_price"]:
                self.inventory[stock_no]["max_price"] = current_price

            drop_from_peak = (
                position["max_price"] - current_price
            ) / position["max_price"]
            total_profit_pct = (
                current_price - position["buy_price"]
            ) / position["buy_price"]

            if drop_from_peak >= 0.025:
                self.order_sell(stock_no, current_price, "移動停損 2.5%")
            elif total_profit_pct >= 0.05:
                self.order_sell(stock_no, current_price, "固定停利 5.0%")
            elif current_time >= datetime.time(13, 20, 0):
                self.order_sell(stock_no, current_price, "尾盤強迫平倉")
            return

        # B. 買進檢查：必須在 09:05 ~ 09:15 之間，且屬於今日選定的最強熱門族群主標的
        if self.active_sector is None:
            return
        target_info = self.sector_matrix[self.active_sector]
        if stock_no != target_info["main"]:
            return

        if not snap.get("open"):
            return
        stock_return = (current_price - snap["open"]) / snap["open"]
        volume_threshold = target_info["avg_vol"] * 0.15

        if (
            (0.025 <= stock_return <= 0.080)
            and (snap["volume"] >= volume_threshold)
            and self.is_tsec_healthy()
        ):
            required_cash = current_price * 1000
            if (
                required_cash <= self.max_budget_per_stock
                and self.cash >= required_cash
            ):
                self.cash -= required_cash
                self.inventory[stock_no] = {
                    "buy_price": current_price,
                    "max_price": current_price,
                    "qty": 1,
                }
                log = f"{current_time.strftime('%H:%M:%S')} 【交易】🟢 觸發動能買進 {target_info['name']}({stock_no}) 1張，價格: {current_price} 元"
                self.trade_log.append(log)

    def order_sell(self, stock_no, price, reason):
        position = self.inventory[stock_no]
        revenue = price * 1000
        self.cash += revenue
        profit_pct = (price - position["buy_price"]) / position["buy_price"] * 100
        log = f"{datetime.datetime.now().strftime('%H:%M:%S')} 【交易】🔴 模擬賣出 ({reason}) 代號: {stock_no} | 價格: {price} 元 | 損益: {profit_pct:+.2f}%"
        self.trade_log.append(log)
        del self.inventory[stock_no]


def update_dashboard_json(bot):
    """將大腦內的所有數據，打包並同步給 Streamlit 看板"""
    dashboard_data = {
        "tsec_current": bot.tsec_current if bot.tsec_current else 22150.0,
        "active_sector": (
            bot.active_sector if bot.active_sector else "等待 09:05 確立風向"
        ),
        "last_update": datetime.datetime.now().strftime("%H:%M:%S"),
        "rankings": (
            bot.latest_rankings_list
            if bot.latest_rankings_list
            else [
                {"族群": "AI先進封裝與載板", "動能得分": 0.0, "平均漲幅(%)": 0.0},
                {"族群": "矽光子與光通訊", "動能得分": 0.0, "平均漲幅(%)": 0.0},
                {"族群": "AI周邊與核心零組件", "動能得分": 0.0, "平均漲幅(%)": 0.0},
            ]
        ),
        "inventory": [
            {
                "股號": k,
                "股名": "AI強勢股",
                "買進價": v["buy_price"],
                "現價": bot.market_snapshot.get(k, {}).get("current", v["buy_price"]),
                "損益(%)": round(
                    (
                        (
                            bot.market_snapshot.get(k, {}).get(
                                "current", v["buy_price"]
                            )
                            - v["buy_price"]
                        )
                        / v["buy_price"]
                    )
                    * 100,
                    2,
                ),
            }
            for k, v in bot.inventory.items()
        ],
        "logs": bot.trade_log[-10:],
    }
    with open("market_state.json", "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=4)


# ==============================================================================
# 數據同步接收與主循環
# ==============================================================================
def fetch_twse_live_data(bot):
    targets = "tsevnp.tw|tse_3189.tw|tse_3037.tw|tse_6515.tw|otc_6510.tw|otc_3163.tw|otc_6442.tw|tse_2345.tw|tse_3013.tw|tse_2368.tw|tse_2408.tw"
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={targets}&_={int(time.time() * 1000)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=4)
        data = res.json()
        if "msgArray" in data:
            for item in data["msgArray"]:
                code = item.get("c")
                current_p = float(item.get("z", item.get("y", 0)))
                open_p = float(item.get("o", item.get("y", 0)))
                vol = int(item.get("v", 0))
                if item.get("ch") == "tsevnp.tw":
                    if bot.tsec_open is None:
                        bot.tsec_open = current_p
                    bot.tsec_current = current_p
                    bot.tsec_history.append((time.time(), current_p))
                elif code in bot.market_snapshot:
                    bot.market_snapshot[code]["open"] = open_p
                    bot.market_snapshot[code]["current"] = current_p
                    bot.market_snapshot[code]["volume"] = vol
    except Exception as e:
        pass


if __name__ == "__main__":
    bot = AIQuantumTradingSystem()
    has_analyzed_today = False
    start_time = datetime.time(9, 0)
    end_time = datetime.time(13, 35)

    # 模擬實盤每 10 秒洗價一次
    for loop in range(10):  # 雲端執行時會持續運行
        now_time = datetime.datetime.now().time()
        fetch_twse_live_data(bot)

        # 到了 09:05 自動判定輪動排行
        if loop >= 2 and not has_analyzed_today:
            bot.run_sector_rotation_analysis()
            has_analyzed_today = True

        # 執行策略
        for stock_code in bot.market_snapshot.keys():
            bot.execute_trading_logic(stock_code, now_time)

        # 寫入 Dashboard JSON 檔案
        update_dashboard_json(bot)
        time.sleep(5)
