import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
# ✅ 請替換成你的 Perplexity API 金鑰
API_KEY = "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"
API_URL = "https://api.perplexity.ai/chat/completions"

industry = "手機產業"

# 你要允許的網站
allowed_domains = [

    "analyticsvidhya.com",
    "thaubing.gcaa.org.tw",
    "cbinsights.com",
    "eetimes.itmedia.co.jp",
    "techanalye.com",
    # "scribd.com",
]

# 產生 Google 搜尋指令
google_queries = "\n".join(
    [f"site:{domain} {industry} 最新消息 OR 報告 OR 趨勢" for domain in allowed_domains]
)

prompt = f"""
今年是2025年，而你是一位50年經驗的專業產業分析師，請即時收集「{industry}」的最新公開資訊，進行產業分析。
請包含：
1. 現況總覽
2. 主要公司（國內外）
3. 未來發展趨勢（至少 2 年）
4. 潛在風險與挑戰
5. 成長趨勢 JSON 格式資料（例如：[{{"year": 2023, "market_cap": 1200}}]）

並且：
- 給我近一周所發生的相關國際大事，依日期列出
- 所有資訊來源必須**僅限於以下網站**：
  {", ".join(allowed_domains)}
- 如果直接訪問這些網站的內容需要註冊或無法取得，請改用 Google 搜尋：
{google_queries}
- 搜尋結果必須來自上述網站的公開頁面，不得引用其他網站
- 每段內容最後需附上原始 URL
"""

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "sonar-pro",
    "messages": [
        {"role": "system", "content": "你是知識淵博的產業分析師"},
        {"role": "user", "content": prompt}
    ],
    "enable_search_classifier": True,
    "search_mode": "web",
    "search_domain_filter": allowed_domains  # ✅ 只會抓取這些網站
}

response = requests.post(API_URL, headers=headers, json=data)

if response.status_code == 200:
    content = response.json()["choices"][0]["message"]["content"]
    print("📘 Perplexity 回覆：\n")
    print(content)
else:
    print("❌ 發生錯誤：", response.status_code)
    print(response.text)
if response.status_code != 200:
    print("❌ 發生錯誤：", response.status_code)
    print(response.text)
    exit()

content = response.json()["choices"][0]["message"]["content"]
print("📘 Perplexity 回覆：\n")
print(content)

# 嘗試從 JSON 回傳中提取來源 URL
try:
    citations = response.json().get("citations", [])
except Exception:
    citations = []

# 如果 citations 空，從內容中嘗試抓 URL
import re
if not citations:
    citations = re.findall(r'https?://[^\s\)]+', content)

# 驗證來源網址是否在允許清單中
def is_allowed(url):
    domain = urlparse(url).netloc
    return any(allowed_domain in domain for allowed_domain in allowed_domains)

bad_sources = [src for src in citations if not is_allowed(src)]
if bad_sources:
    print("\n⚠️ 發現不在允許清單的來源：", bad_sources)
else:
    print("\n✅ 所有來源的 domain 都在允許清單內")

# 驗證內容是否真的存在於該 URL
def verify_content(url, snippet):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        return snippet[:50] in soup.get_text()
    except Exception:
        return False

print("\n🔍 驗證來源內容...")
for url in citations:
    if is_allowed(url):
        snippet_match = verify_content(url, content)
        print(f"{url} → {'✅ 內容匹配' if snippet_match else '⚠️ 內容可能不一致'}")