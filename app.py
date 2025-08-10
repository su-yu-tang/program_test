from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "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"
API_URL = "https://api.perplexity.ai/chat/completions"

@app.route('/analyze-industry', methods=['POST'])
def analyze_industry():
    data = request.get_json()
    industry = data.get("industry")

    if not industry:
        return jsonify({"error": "請提供產業名稱 'industry'"}), 400

    prompt = f"""
你是一位專業產業分析師，請即時收集「{industry}」的最新公開資訊，進行產業分析。
請包含以下內容，且特別要求提供可視化用的 JSON 格式數據：

1. 現況總覽（以文字說明）
2. 主要公司（列出全球前五大）
3. 未來發展趨勢（預測未來 2~3 年的技術、需求與產值變化）
4. 潛在風險與挑戰（列舉 3 項）
5. 請提供{industry}的歷年量化指標，並以 JSON 陣列格式提供，格式如下：

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

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "你是知識淵博的產業分析師"},
            {"role": "user", "content": prompt}
        ],
        "enable_search_classifier": True
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        return jsonify({"result": content})
    else:
        return jsonify({"error": "API 請求失敗", "status_code": response.status_code, "detail": response.text}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
