import json, requests, time, concurrent.futures

# 扩充更全的高质量聚合源，确保抓取基数足够大
SOURCE_URLS = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json",
    "https://raw.githubusercontent.com/FongMi/Release/main/levon/Index.json",
    "https://raw.githubusercontent.com/yqmkk/my-tv-config/main/tv.json",
    "https://raw.githubusercontent.com/1351064089/my-tv-config/main/tv.json",
    "https://itvbox.cc/tvbox/sources/my.json"
]

# 定义真实备用源（当抓取不足50个时，循环使用这些真实站名填充）
BACKUP_SITES = [
    {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "量子资源", "detail": "https://cj.lziapi.com"},
    {"api": "https://cj.ffzyapi.com/api.php/provide/vod", "name": "非凡资源", "detail": "https://cj.ffzyapi.com"},
    {"api": "https://video.gture.top/api.php/provide/vod", "name": "光速资源", "detail": "https://video.gture.top"},
    {"api": "https://bfzyapi.com/api.php/provide/vod", "name": "暴风资源", "detail": "https://bfzyapi.com"},
    {"api": "https://cj.huaceapi.com/api.php/provide/vod", "name": "华策极清", "detail": "https://cj.huaceapi.com"}
]

def evaluate_site(site):
    try:
        start_time = time.time()
        # 严格 2 秒超时，确保只有极速站入选
        res = requests.get(site['api'], timeout=2)
        if res.status_code == 200 and "vod" in res.text:
            delay = time.time() - start_time
            # 给大厂站（CDN强）加权，让它们排在前面
            score = delay
            if any(fast in site['api'] for fast in ['lzi', 'ffzy', 'huace', 'bfzy']):
                score -= 0.3
            return (score, site)
    except:
        pass
    return None

def main():
    all_raw_sites = []
    for url in SOURCE_URLS:
        try:
            data = requests.get(url, timeout=8).json()
            for s in data.get("sites", []):
                # 只采集 CMS 接口
                if s.get("type") in [0, 1] and "api.php" in s.get("api", ""):
                    # 清理站名中的杂质
                    clean_name = s["name"].replace("资源", "").replace("采集", "").strip()
                    all_raw_sites.append({
                        "api": s["api"],
                        "name": clean_name if clean_name else "未知站点",
                        "detail": s["api"].split("api.php")[0]
                    })
        except: continue

    # 去重
    unique_sites = {s['api']: s for s in all_raw_sites}.values()

    # 并发测速
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = [r for r in executor.map(evaluate_site, unique_sites) if r]
        
    results.sort(key=lambda x: x[0])
    top_50 = [r[1] for r in results[:50]]

    # 填充逻辑优化：如果不足50个，从真实备份源中循环提取
    if len(top_50) < 50:
        backup_idx = 0
        while len(top_50) < 50:
            top_50.append(BACKUP_SITES[backup_idx % len(BACKUP_SITES)])
            backup_idx += 1

    config = {
        "cache_time": 7200,
        "api_site": {f"site_{i:02d}": s for i, s in enumerate(top_50)},
        "custom_category": [
            {"name": "🔥 4K·极清", "type": "movie", "query": "4K"},
            {"name": "🎞️ 华语大片", "type": "movie", "query": "华语"},
            {"name": "🌸 2026新番", "type": "anime", "query": "2026"},
            {"name": "🎥 欧美蓝光", "type": "movie", "query": "蓝光"}
        ]
    }
    
    with open("deco.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
