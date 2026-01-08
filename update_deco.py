import json, requests, time, base58, re
from urllib.parse import urlparse

# 2026年国内最稳、带宽最高的顶级大厂源白名单
# 这些站由国内高速CDN分发，大屏端播放极速
PREMIUM_SITES = [
    {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "🔥量子高清4K"},
    {"api": "https://cj.ffzyapi.com/api.php/provide/vod", "name": "🔥非凡秒开"},
    {"api": "https://cj.huaceapi.com/api.php/provide/vod", "name": "华策极清"},
    {"api": "https://video.gture.top/api.php/provide/vod", "name": "光速蓝光"},
    {"api": "https://bfzyapi.com/api.php/provide/vod", "name": "暴风影视"},
    {"api": "https://www.605zy.cc/api.php/provide/vod", "name": "605资源"},
    {"api": "https://api.tianyiapi.com/api.php/provide/vod", "name": "天翼高清"},
    {"api": "https://jszyapi.com/api.php/provide/vod", "name": "极速资源"},
    {"api": "https://www.feisuzyapi.com/api.php/provide/vod", "name": "飞速资源"},
    {"api": "https://api.kkzy.tv/api.php/provide/vod", "name": "快看资源"},
    {"api": "https://subocaiji.com/api.php/provide/vod", "name": "速播资源"},
    {"api": "https://cj.sdzyapi.com/api.php/provide/vod", "name": "闪电资源"},
    {"api": "https://www.kuaichezy.com/api.php/provide/vod", "name": "快车资源"},
    {"api": "https://api.123zy.com/api.php/provide/vod", "name": "123资源"},
    {"api": "https://www.jingchengzy.com/api.php/provide/vod", "name": "精品资源"}
]

# 备用爬取池
SOURCE_URLS = [
    "https://gh-proxy.com/https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json",
    "https://raw.liucn.cc/box/m.json",
    "https://itvbox.cc/tvbox/sources/my.json"
]

def main():
    final_50 = []
    seen_domains = set()

    # 1. 首先填入硬核优选源
    for s in PREMIUM_SITES:
        domain = urlparse(s['api']).netloc
        if domain not in seen_domains:
            s['detail'] = s['api'].split("api.php")[0]
            final_50.append(s)
            seen_domains.add(domain)

    # 2. 从全网源中补齐剩下的位置
    for url in SOURCE_URLS:
        if len(final_50) >= 50: break
        try:
            r = requests.get(url, timeout=10)
            data = json.loads(r.text.encode('utf-8').decode('utf-8-sig'))
            for s in data.get("sites", []):
                if len(final_50) >= 50: break
                api = s.get("api", "")
                if s.get("type") in [0, 1] and "api.php" in api:
                    domain = urlparse(api).netloc
                    if domain not in seen_domains:
                        name = re.sub(r'\(.*?\)|\[.*?\]|资源|采集|极速|优质', '', s["name"]).strip()
                        final_50.append({
                            "api": api,
                            "name": name if name else "备用线路",
                            "detail": api.split("api.php")[0]
                        })
                        seen_domains.add(domain)
        except: continue

    # 确保正好 50 个，不多不少
    final_50 = final_50[:50]

    config = {
        "cache_time": 7200,
        "api_site": {f"site_{i:02d}": s for i, s in enumerate(final_50)},
        "custom_category": [
            {"name": "🔥 4K·极清", "type": "movie", "query": "4K"},
            {"name": "🎞️ 华语精选", "type": "movie", "query": "华语"},
            {"name": "🌸 2026新番", "type": "anime", "query": "2026"}
        ]
    }

    # 保存 JSON
    with open("deco.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # 生成 Base58
    compact = json.dumps(config, ensure_ascii=False).encode('utf-8')
    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(base58.b58encode(compact).decode('utf-8'))

if __name__ == "__main__":
    main()
