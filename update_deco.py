import json, requests, time, concurrent.futures, base58, re
from urllib.parse import urlparse

# 定义 2026 年已知的高带宽大厂源（这些源虽然延迟高，但能扛住 4K 流量）
# 只要这些站在 10s 内有响应，就强制排在最前面
PRIORITY_DOMAINS = [
    "lziapi.com", "ffzyapi.com", "huaceapi.com", "suoniapi.com", 
    "gture.top", "bfzyapi.com", "kkzy.tv", "feisuzyapi.com",
    "snzypm.com", "123zy.com", "zuidapi.com", "wolongzy.cc"
]

DYNAMIC_SOURCES = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json",
    "https://itvbox.cc/tvbox/sources/my.json",
    "https://raw.liucn.cc/box/m.json"
]

def check_site_bandwidth_focus(site):
    """
    高宽容度检测：
    1. 延迟 100ms 和 1000ms 对我们来说没区别。
    2. 只要能通，且在白名单内，就是顶级源。
    """
    try:
        start = time.time()
        # 将超时放宽到 8 秒，确保那些“慢热型”的高速站不被剔除
        res = requests.get(site['api'], timeout=8)
        if res.status_code == 200 and "vod" in res.text:
            domain = urlparse(site['api']).netloc
            # 权重计算：白名单 0 分，普通站 100 分
            weight = 0 if any(k in domain for k in PRIORITY_DOMAINS) else 100
            return (weight, site)
    except:
        pass
    return None

def main():
    raw_pool = []
    # 结合动态抓取和你提供的蓝本数据
    for url in DYNAMIC_SOURCES:
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            for s in data.get("sites", []):
                if s.get("type") in [0, 1] and "api.php" in s.get("api", ""):
                    name = re.sub(r'\(.*?\)|\[.*?\]|资源|采集|极速', '', s["name"]).strip()
                    raw_pool.append({"api": s["api"], "name": name or "海外高速源"})
        except: continue

    # 严格域名去重：50个坑位必须是50个不同的出口
    unique_sites = {urlparse(s['api']).netloc: s for s in raw_pool}.values()

    # 并发检测
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        results = [r for r in executor.map(check_site_bandwidth_focus, unique_sites) if r]
    
    # 排序逻辑：优先保白名单，剩下按发现顺序补齐（不按延迟排）
    results.sort(key=lambda x: x[0])
    top_50 = [r[1] for r in results[:50]]

    # 兜底填充
    while len(top_50) < 50:
        top_50.append({"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "量子4K保底"})

    # 整理 DecoTV 格式
    for i, s in enumerate(top_50):
        s['detail'] = s['api'].split("api.php")[0]
        # 给高带宽源打上钻石标记
        if any(k in s['api'] for k in PRIORITY_DOMAINS):
            s['name'] = f"💎{s['name']}"

    config = {
        "cache_time": 9200,
        "api_site": {f"api_{i+1}": s for i, s in enumerate(top_50)},
        "custom_category": [
            {"name": "🎞️ 115·网盘高清", "type": "movie", "query": "115"},
            {"name": "🔥 4K·极清专区", "type": "movie", "query": "4K"},
            {"name": "📺 华语精选", "type": "movie", "query": "华语"}
        ]
    }

    # 写入文件
    with open("deco.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    compact = json.dumps(config, ensure_ascii=False).encode('utf-8')
    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(base58.b58encode(compact).decode('utf-8'))

if __name__ == "__main__":
    main()
