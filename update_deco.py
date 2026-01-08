import json, requests, time, concurrent.futures, base58

SOURCE_URLS = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json",
    "https://raw.githubusercontent.com/FongMi/Release/main/levon/Index.json",
    "https://raw.githubusercontent.com/yqmkk/my-tv-config/main/tv.json"
]

BACKUP_SITES = [
    {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "量子资源", "detail": "https://cj.lziapi.com"},
    {"api": "https://cj.ffzyapi.com/api.php/provide/vod", "name": "非凡资源", "detail": "https://cj.ffzyapi.com"},
    {"api": "https://video.gture.top/api.php/provide/vod", "name": "光速资源", "detail": "https://video.gture.top"},
    {"api": "https://bfzyapi.com/api.php/provide/vod", "name": "暴风资源", "detail": "https://bfzyapi.com"}
]

def evaluate_site(site):
    try:
        start = time.time()
        res = requests.get(site['api'], timeout=2)
        if res.status_code == 200 and "vod" in res.text:
            delay = time.time() - start
            score = delay - 0.3 if any(k in site['api'] for k in ['lzi', 'ffzy', 'huace']) else delay
            return (score, site)
    except: pass
    return None

def main():
    raw_sites = []
    for url in SOURCE_URLS:
        try:
            data = requests.get(url, timeout=5).json()
            for s in data.get("sites", []):
                if s.get("type") in [0, 1] and "api.php" in s.get("api", ""):
                    name = s["name"].replace("资源", "").replace("采集", "").strip()
                    raw_sites.append({"api": s["api"], "name": name, "detail": s["api"].split("api.php")[0]})
        except: continue

    unique_sites = {s['api']: s for s in raw_sites}.values()
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as exe:
        results = sorted([r for r in exe.map(evaluate_site, unique_sites) if r], key=lambda x: x[0])
    
    top_50 = [r[1] for r in results[:50]]
    # 强制补齐50个真实名称站点
    while len(top_50) < 50:
        top_50.append(BACKUP_SITES[len(top_50) % len(BACKUP_SITES)])

    config = {
        "cache_time": 7200,
        "api_site": {f"site_{i:02d}": s for i, s in enumerate(top_50)},
        "custom_category": [
            {"name": "🔥 4K·极清", "type": "movie", "query": "4K"},
            {"name": "🌸 2026新番", "type": "anime", "query": "2026"}
        ]
    }
    
    # 1. 保存普通 JSON
    with open("deco.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        
    # 2. 生成 Base58 编码字符串并保存
    compact_json = json.dumps(config, ensure_ascii=False).encode('utf-8')
    b58_str = base58.b58encode(compact_json).decode('utf-8')
    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(b58_str)

if __name__ == "__main__":
    main()
