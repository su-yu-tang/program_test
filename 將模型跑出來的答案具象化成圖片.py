import requests
import json
import matplotlib.pyplot as plt

# ✅ 替換成你的 Perplexity API 金鑰
API_KEY = "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"
API_URL = "https://api.perplexity.ai/chat/completions"

# ✅ 分析產業
industry = "手機產業"

# ✅ 建立 prompt（更具結構化、可視化需求）
prompt = f"""
你是一位專業產業分析師，請即時收集「{industry}」的最新公開資訊，進行產業分析。
請包含以下內容，且特別要求提供可視化用的 JSON 格式數據：

1. 現況總覽（以文字說明）
2. 主要公司（列出全球前五大）
3. 未來發展趨勢（預測未來 2~3 年的技術、需求與產值變化）
4. 潛在風險與挑戰（列舉 3 項）
5. 請提供手機產業的歷年量化指標，並以 JSON 陣列格式提供，格式如下：

[
  {{
    "year": 2021,
    "shipment_million_units": 1350,
    "market_share_top3_percent": 65.2,
    "industry_revenue_billion_usd": 420,
    "growth_rate_percent": 3.5
  }},
  ...
]

6. 近一週與「{industry}」相關的國際重大新聞，以日期分類列表呈現（格式如下）：
[
  {{
    "date": "2025-07-30",
    "event": "蘋果公司宣布新一代摺疊機開發完成"
  }},
  ...
]
"""

# ✅ 發送 API 請求
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "sonar",
    "messages": [
        {"role": "system", "content": "你是知識淵博的產業分析師"},
        {"role": "user", "content": prompt}
    ],
    "enable_search_classifier": True,
}

response = requests.post(API_URL, headers=headers, json=data)

# ✅ 處理回傳內容
if response.status_code == 200:
    content = response.json()["choices"][0]["message"]["content"]
    print("📘 Perplexity 回覆內容：\n")
    print(content)

    # 嘗試自動擷取 JSON 量化資料區段
    import re

    json_match = re.search(r'\[\s*{[^]]+}\s*\]', content)
    if json_match:
        try:
            json_data = json.loads(json_match.group())
            print("\n📊 抽取的 JSON 數據：")
            print(json.dumps(json_data, indent=2))

            # ✅ 可視化出貨量與營收
            years = [item["year"] for item in json_data]
            shipments = [item["shipment_million_units"] for item in json_data]
            revenues = [item["industry_revenue_billion_usd"] for item in json_data]

            plt.figure(figsize=(10, 5))
            plt.plot(years, shipments, marker='o', label='shipments (百萬台)')
            plt.plot(years, revenues, marker='s', label='revenues (十億美元)')
            plt.title(f"{industry} 出貨量與產業營收趨勢")
            plt.xlabel("年份")
            plt.ylabel("數值")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        except json.JSONDecodeError:
            print("⚠️ 無法解析 JSON，請手動檢查格式。")
    else:
        print("⚠️ 沒有找到符合格式的 JSON 區塊。")

else:
    print("❌ 發生錯誤：", response.status_code)
    print(response.text)
