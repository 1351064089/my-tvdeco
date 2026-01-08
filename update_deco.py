import json, requests, time, concurrent.futures, base58, re
from urllib.parse import urlparse

# 2026年精选源，涵盖全网 90% 以上的采集站
SOURCE_URLS = [
    "https://gh-proxy.com/https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json",
    "https://raw.liucn.cc/box/m.json",
    "https://itvbox.cc/tvbox/sources/my.json",
    "https://raw.githubusercontent.com/FongMi/Release/main/levon/Index.json"
]

BACKUP_SITES = [
    {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "量子高速", "detail": "https://cj.lziapi.com"},
    {"api": "https://cj.ffzyapi.com/api.php/provide/vod", "name": "非凡极速", "detail": "https://cj.ffzyapi.com"},
    {"api": "https://cj.huaceapi.com/api.php/provide/vod", "name": "华策4K", "detail": "https://cj.huaceapi.com"},
    {"api": "https://video.gture.top/api.php/provide/vod", "name": "光速蓝光", "detail": "https://video.gture.top"},
    {"api": "https://bfzyapi.com/api.php/provide/vod", "name": "暴风影音", "detail": "https://bfzyapi.com"}
]

def check_site(site):
    try:
        start = time.time()
        # 只要测速通了，并且包含 vod 字样说明接口正常
        res = requests.get(site['api'], timeout=2.5)
        if res.status_code == 200 and "vod" in res.text:
            delay = time.time() - start
            return (delay, site)
    except: pass
    return None

def main():
    pool = []
    for url in SOURCE_URLS:
        try:
            r = requests.get(url, timeout=10)
            data = json.loads(r.text.encode('utf-8').decode('utf-8-sig'))
            for s in data.get("sites", []):
                if s.get("type") in [0, 1] and "api.php" in s.get("api", ""):
                    name = re.sub(r'\(.*?\)|\[.*?\]|资源|采集|极速|优质|官网', '', s["name"]).strip()
                    pool.append({"api": s["api"], "name": name if name else "极速源"})
        except: continue

    # --- 核心去重逻辑 ---
    # 使用域名作为 Key，确保同一个服务器只出现一次
    domain_unique_pool = {}
    for s in pool:
        domain = urlparse(s['api']).netloc
        # 如果域名重复，只保留名字长的（通常名字更完整）
        if domain not in domain_unique_pool or len(s['name']) > len(domain_unique_pool[domain]['name']):
            domain_unique_pool[domain] = s
    
    # --- 多线程并发测速 ---
    unique_list = list(domain_unique_pool.values())
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = sorted([r for r in executor.map(check_site, unique_list) if r], key=lambda x: x[0])
    
    top_list = [r[1] for r in results[:50]]

    # --- 强制补齐与细节处理 ---
    while len(top_list) < 50:
        top_list.append(BACKUP_SITES[len(top_list) % len(BACKUP_SITES)])

    # 规范化输出内容
    for i, s in enumerate(top_list):
        s['detail'] = s['api'].split("api.php")[0]
        # 给前 5 个最快的站加个火苗图标
        if i < 5: s['name'] = f"🔥{s['name']}"

    config = {
        "cache_time": 7200,
        "api_site": {f"site_{i:02d}": s for i, s in enumerate(top_list)},
        "custom_category": [
            {"name": "🔥 4K·极清", "type": "movie", "query": "4K"},
            {"name": "🎞️ 华语大片", "type": "movie", "query": "华语"},
            {"name": "🌸 2026新番", "type": "anime", "query": "2026"}
        ]
    }

    with open("deco.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    compact = json.dumps(config, ensure_ascii=False).encode('utf-8')
    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(base58.b58encode(compact).decode('utf-8'))

if __name__ == "__main__":
    main()
