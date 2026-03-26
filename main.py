import yfinance as yf
import requests
import os
from datetime import datetime

# 1. 从 GitHub Secrets 安全读取飞书 Webhook 地址
FEISHU_WEBHOOK = os.environ.get('FEISHU_WEBHOOK')

# 2. 配置持仓信息（你可以随时在这里修改数量）
PORTFOLIO = {
    "688619.SS": {
        "name": "云天励飞", "unit": "￥", 
        "extra": "RMBIII剩余持股数量52,347股。"
    },
    "2471.HK": {
        "name": "找钢", "unit": "HKD", 
        "extra": "USDI剩余可卖52,919,124。"
    },
    "2438.HK": {
        "name": "出门问问", "unit": "HKD", 
        "extra": "教育今日无减持，剩余数量11,652,946股；\nUSDI持有43,113,580股。"
    },
    "1611.HK": {
        "name": "huobi香港公司股票", "unit": "HKD", 
        "extra": "USDI仍持有5,113,265股。"
    },
    "WDH": {
        "name": "水滴", "unit": "$", 
        "extra": "RMBIV持有3,014,400 ADS，USDV持有516,800 ADS。"
    },
    "XCH": {
        "name": "智充科技", "unit": "$", 
        "extra": "USDIV已转换ADR 398,064 (1/10)，未转换ADR 3,582,583 (9/10)。"
    },
    "RBLX": {
        "name": "Roblox", "unit": "$", 
        "extra": "USDIV持有数量10,824。"
    },
    "YSG": {
        "name": "Perfect Diary", "unit": "$", 
        "extra": "USDIV已转换ADR 2,777,895 (1/4)， 未转换ADR 8,333,685 (3/4)。"
    },
    "YMT": {
        "name": "一亩田", "unit": "$", 
        "extra": "USDIV已全部转换ADR 3,104,106。"
    }
}

def get_report():
    # 获取当前日期格式
    today_str = datetime.now().strftime("%Y年%m月%d日")
    report_content = f"{today_str}\n\n"
    
    for ticker, info in PORTFOLIO.items():
        try:
            stock = yf.Ticker(ticker)
            # 获取最近2天数据计算涨跌幅
            hist = stock.history(period="2d")
            if len(hist) < 2:
                continue
                
            close_price = round(hist['Close'].iloc[-1], 2)
            prev_close = hist['Close'].iloc[-2]
            change_pct = ((close_price - prev_close) / prev_close) * 100
            
            # 🔴 代表涨，🟢 代表跌
            icon = "🔴" if change_pct >= 0 else "🟢"
            trend_str = "涨幅" if change_pct >= 0 else "跌幅"
            
            # 拼接单条股票信息
            report_content += f"{icon}{info['name']} ({ticker if '.HK' in ticker else ''})：收盘价{info['unit']} {close_price}，{trend_str}{abs(round(change_pct, 2))}%；\n"
            report_content += f"{info['extra']}\n\n"
            
        except Exception as e:
            report_content += f"⚠️ {info['name']} 数据获取失败: {e}\n\n"
            
    return report_content

def send_to_feishu(text):
    if not FEISHU_WEBHOOK:
        print("错误：未找到 FEISHU_WEBHOOK 环境变量")
        return
    
    payload = {
        "msg_type": "text",
        "content": {"text": text}
    }
    response = requests.post(FEISHU_WEBHOOK, json=payload)
    print(f"推送结果: {response.status_code}, {response.text}")

if __name__ == "__main__":
    final_report = get_report()
    send_to_feishu(final_report)
