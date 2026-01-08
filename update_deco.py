import json, requests, time, concurrent.futures, base58, re
from urllib.parse import urlparse

# 1. 动态抓取源（2026年最活跃的聚合订阅）
DYNAMIC_SOURCES = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json",
    "https://itvbox.cc/tvbox/sources/my.json",
    "https://raw.liucn.cc/box/m.json"
]

# 2. 你的核心保底库（精选自你提供的列表）
CORE_SITES = [
    {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "量子资源"},
    {"api": "https://api.ffzyapi.com/api.php/provide/vod", "name": "非凡影视"},
    {"api": "https://jszyapi.com/api.php/provide/vod", "name": "极速资源"},
    {"api": "https://api.guangsuapi.com/api.php/provide/vod", "name": "光速资源"},
    {"api": "https://suoniapi.com/api.php/provide/vod", "name": "索尼资源"},
    {"api": "https://bfzyapi.com/api.php/provide/vod", "name": "暴风高清"},
    {"api": "https://hhzyapi.com/api.php/provide/vod", "name": "豪华资源"},
    {"api": "https://api.1080zyku.com/inc/api_mac10.php", "name": "1080资源"}
]

def check_site(site):
    """测速并验证接口有效性"""
    try:
        start = time.time()
        # 增加超时限制，太慢的直接不要
        res = requests.get(site['api'], timeout=2)
        if res.status_code == 200 and ("vod" in res.text or "list" in res.text):
            return (time.time() - start, site)
    except:
        pass
    return None

def main():
    all_raw_sites = CORE_SITES.copy()

    # 自动抓取全网最新地址
    for url in DYNAMIC_SOURCES:
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            for s in data.get("sites", []):
                if s.get("type") in [0, 1] and "api.php" in s.get("api", ""):
                    name = re.sub(r'\(.*?\)|\[.*?\]|资源|采集', '', s["name"]).strip()
                    all_raw_sites.append({"api": s["api"], "name": name or "自动发现"})
        except:
            continue

    # 域名去重（核心步骤：防止重复站占据50个名额）
    unique_dict = {}
    for s in all_raw_sites:
        domain = urlparse(s['api']).netloc
        if domain and domain not in unique_dict:
            unique_dict[domain] = s

    # 并发测速筛选（前50名）
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = [r for r in executor.map(check_site, unique_dict.values()) if r]
    
    # 按速度排序，取前50个
    results.sort(key=lambda x: x[0])
    top_50 = [r[1] for r in results[:50]]

    # 补齐至50个（如果抓到的不够，就循环补齐）
    while len(top_50) < 50:
        top_50.append(CORE_SITES[len(top_50) % len(CORE_SITES)])

    # 整理格式
    for i, s in enumerate(top_50):
        s['detail'] = s['api'].split("api.php")[0]
        if i < 5: s['name'] = f"🚀{s['name']}" # 给最快的5个加标记

    config = {
        "cache_time": 9200,
        "api_site": {f"api_{i+1}": s for i, s in enumerate(top_50)},
        "custom_category": [
            {"name": "🎞️ 115·蓝光", "type": "movie", "query": "115"},
            {"name": "🔥 4K·极清", "type": "movie", "query": "4K"},
            {"name": "🌸 2026新番", "type": "anime", "query": "2026"}
        ]
    }

    # 导出文件
    with open("deco.json", "w", encoding="utf-8") as f
