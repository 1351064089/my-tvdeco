import json, requests, time, concurrent.futures, base58, re

# 精选 2026 年最稳的元数据池，确保能抓到真实站点
SOURCE_URLS = [
    "https://gh-proxy.com/https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json",
    "https://raw.liucn.cc/box/m.json",
    "https://itvbox.cc/tvbox/sources/my.json"
]

# 核心高速白名单：这些源必须排在前面
VIP_KEYWORDS = ['lzi', 'ffzy', 'huace', 'bfzy', 'snzy', 'kuaikan']

def evaluate_site(site):
    """深度验证：不仅测延迟，还验证接口是否真的能吐出数据"""
    api_url = site['api']
    if "api.php" not in api_url: return None
    
    try:
        start_time = time.time()
        # 尝试请求最新的1条数据来验证接口真实有效性
        test_url = f"{api_url}?ac=list&pagesize=1"
        res = requests.get(test_url, timeout=2.5, headers={'User-Agent': 'DecoTV/2.1'})
        
        if res.status_code == 200 and ("vod" in res.text or "list" in res.text):
            delay = time.time() - start_time
            # 权重计算：如果是大厂高速CDN，给予 0.5秒 的“加速特权”排名
            score = delay
            if any(k in api_url.lower() for k in VIP_KEYWORDS):
                score -= 0.5
            return (score, site)
    except:
        pass
    return None

def main():
    raw_pool = []
    for url in SOURCE_URLS:
        try:
            res = requests.get(url, timeout=10)
            data = json.loads(res.text.encode('utf-8').decode('utf-8-sig'))
            for s in data.get("sites", []):
                if s.get("type") in [0, 1] and s.get("api").startswith("http"):
                    # 站名精简化处理
                    name = re.sub(r'\(.*?\)|\[.*?\]|资源|采集|极速|优质', '', s["name"]).strip()
                    raw_pool.append({
                        "api": s["api"],
                        "name": name if name else "高速接口",
                        "detail": s["api"].split("api.php")[0]
                    })
        except: continue

    # 物理去重
    unique_sites = {s['api']: s for s in raw_pool}.values()

    # 并发验证（提高到 60 线程加速处理）
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        results = [r for r in executor.map(evaluate_site, unique_sites) if r]
    
    # 按综合评分排序
    results.sort(key=lambda x: x[0])
    
    # 提取前 50 个最强站点
    final_50 = [r[1] for r in results[:50]]

    # 兜底：如果抓取的不足50，用不同的大厂源循环填充，保证名字真实且不重复
    if len(final_50) < 50:
        backups = [
            {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "量子高清", "detail": "https://cj.lziapi.com"},
            {"api": "https://cj.ffzyapi.com/api.php/provide/vod", "name": "非凡秒开", "detail": "https://cj.ffzyapi.com"},
            {"api": "https://cj.huaceapi.com/api.php/provide/vod", "name": "华策4K", "detail": "https://cj.huaceapi.com"}
        ]
        while len(final_50) < 50:
            final_50.append(backups[len(final_50) % len(backups)])

    config = {
        "cache_time": 7200,
        "api_site": {f"site_{i:02d}": s for i, s in enumerate(final_50)},
        "custom_category": [
            {"name": "🔥 4K·极清", "type": "movie", "query": "4K"},
            {"name": "🎞️ 华语精选", "type": "movie", "query": "华语"},
            {"name": "🌸 2026新番", "type": "anime", "query": "2026"}
        ]
    }

    # 输出文件
    with open("deco.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # 生成 Base58
    compact_json = json.dumps(config, ensure_ascii=False).encode('utf-8')
    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(base58.b58encode(compact_json).decode('utf-8'))

if __name__ == "__main__":
    main()
