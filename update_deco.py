import json, requests, time, concurrent.futures

# 抓取的 TVBox 聚合源地址
SOURCE_URLS = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json",
    "https://raw.githubusercontent.com/FongMi/Release/main/levon/Index.json"
]

def check_speed(site):
    try:
        start = time.time()
        # 仅测试连通性，超时设为 2 秒确保极速
        res = requests.get(site['api'], timeout=2)
        if res.status_code == 200:
            return (time.time() - start, site)
    except: pass
    return None

def main():
    all_sites = []
    for url in SOURCE_URLS:
        try:
            data = requests.get(url, timeout=5).json()
            for s in data.get("sites", []):
                # 只采集标准 CMS 接口 (type 0 或 1)
                if s.get("type") in [0, 1] and "api.php" in s.get("api", ""):
                    all_sites.append({"api": s["api"], "name": s["name"], "detail": s["api"].split("api.php")[0]})
        except: continue

    # 测速排序
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        results = [r for r in executor.map(check_speed, all_sites) if r]
        results.sort(key=lambda x: x[0])
        fast_sites = [r[1] for r in results[:50]] # 筛选前 50 个

    config = {
        "cache_time": 9200,
        "api_site": {f"site_{i}": s for i, s in enumerate(fast_sites)},
        "custom_category": [
            {"name": "4K极清", "type": "movie", "query": "4K"},
            {"name": "2026新番", "type": "anime", "query": "2026"},
            {"name": "华语精选", "type": "movie", "query": "华语"}
        ]
    }
    with open("deco.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
