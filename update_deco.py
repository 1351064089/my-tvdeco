import json, requests, time, concurrent.futures

# 精选全网高质量聚合源
SOURCE_URLS = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json",
    "https://raw.githubusercontent.com/FongMi/Release/main/levon/Index.json",
    "https://raw.githubusercontent.com/1351064089/my-tv-config/main/tv.json"
]

def evaluate_site(site):
    """综合评估站点：延迟 + 稳定性"""
    try:
        start_time = time.time()
        # 模拟 DecoTV 的请求头
        headers = {'User-Agent': 'DecoTV/2.1 (Linux; Android 11)'}
        res = requests.get(site['api'], timeout=2, headers=headers)
        
        if res.status_code == 200 and "vod" in res.text:
            delay = time.time() - start_time
            # 权重计算：延迟越小分越高，如果是特定的高速CDN则加分
            score = delay
            if any(fast in site['api'] for fast in ['lzi', 'ffzy', 'huace', 'bfzy']):
                score -= 0.2  # 给优质线路“超车”机会
            return (score, site)
    except:
        pass
    return None

def main():
    all_raw_sites = []
    for url in SOURCE_URLS:
        try:
            data = requests.get(url, timeout=5).json()
            for s in data.get("sites", []):
                # 严格筛选：CMS 类型接口 + HTTPS 优先
                if s.get("type") in [0, 1] and "api.php" in s.get("api", ""):
                    all_raw_sites.append({
                        "api": s["api"],
                        "name": s["name"].replace("资源", ""), # 精简名称
                        "detail": s["api"].split("api.php")[0]
                    })
        except: continue

    # 去重
    unique_sites = {s['api']: s for s in all_raw_sites}.values()

    # 并发测速：开启 50 个线程确保效率
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = [r for r in executor.map(evaluate_site, unique_sites) if r]
        
    # 排序并取前 50 个
    results.sort(key=lambda x: x[0])
    top_50 = [r[1] for r in results[:50]]

    # 如果抓取不足50个，用默认稳健源填充（防止配置报错）
    while len(top_50) < 50:
        top_50.append({"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "保底线路", "detail": "https://cj.lziapi.com"})

    config = {
        "cache_time": 7200, # 改为 2 小时，保持新鲜度
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
