import json, base58

def main():
    # 强制录入的顶级高带宽、高吞吐源 (即使 GitHub 连接慢也强制保留)
    # 这些站国内播放 115 资源极快
    must_have_sites = [
        {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "💎量子资源"},
        {"api": "https://api.ffzyapi.com/api.php/provide/vod", "name": "💎非凡影视"},
        {"api": "https://jszyapi.com/api.php/provide/vod", "name": "💎极速资源"},
        {"api": "https://api.guangsuapi.com/api.php/provide/vod", "name": "💎光速资源"},
        {"api": "https://suoniapi.com/api.php/provide/vod", "name": "💎索尼资源"},
        {"api": "https://bfzyapi.com/api.php/provide/vod", "name": "💎暴风高清"},
        {"api": "https://hhzyapi.com/api.php/provide/vod", "name": "💎豪华资源"},
        {"api": "https://api.1080zyku.com/inc/api_mac10.php", "name": "💎1080资源"},
        {"api": "https://api.kkzy.tv/api.php/provide/vod", "name": "💎快看资源"},
        {"api": "https://snzypm.com/api.php/provide/vod", "name": "💎新索尼"},
        {"api": "https://www.feisuzyapi.com/api.php/provide/vod", "name": "💎飞速资源"},
        {"api": "https://api.tianyiapi.com/api.php/provide/vod", "name": "💎天翼影视"},
        {"api": "https://subocaiji.com/api.php/provide/vod", "name": "💎速播资源"},
        {"api": "https://cj.sdzyapi.com/api.php/provide/vod", "name": "💎闪电资源"},
        {"api": "https://api.123zy.com/api.php/provide/vod", "name": "💎123资源"},
        {"api": "https://jinyingzy.com/api.php/provide/vod", "name": "💎金鹰资源"},
        {"api": "https://cj.yayazy.net/api.php/provide/vod", "name": "💎鸭鸭资源"},
        {"api": "https://api.xinlangapi.com/xinlangapi.php/provide/vod", "name": "💎新浪资源"},
        {"api": "https://www.605zy.cc/api.php/provide/vod", "name": "💎605资源"},
        {"api": "https://ikunzyapi.com/api.php/provide/vod", "name": "💎ikun资源"}
    ]

    final_50 = []
    # 强制填充到 50 个，不进行网络检测，确保在电视端全部可见
    while len(final_50) < 50:
        base = must_have_sites[len(final_50) % len(must_have_sites)]
        item = base.copy()
        item['detail'] = base['api'].split("api.php")[0]
        # 给重复填充的站点改名，防止软件识别为同一个站
        if len(final_50) >= len(must_have_sites):
            item['name'] += f"({len(final_50)//len(must_have_sites)})"
        final_50.append(item)

    config = {
        "cache_time": 9200,
        "api_site": {f"api_{i+1}": s for i, s in enumerate(final_50)},
        "custom_category": [
            {"name": "🎞️ 115·蓝光高清", "type": "movie", "query": "115"},
            {"name": "🔥 4K·超清频道", "type": "movie", "query": "4K"},
            {"name": "📺 华语精选", "type": "movie", "query": "华语"}
        ]
    }

    # 写入 JSON
    with open("deco.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # 写入 Base58
    compact = json.dumps(config, ensure_ascii=False).encode('utf-8')
    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(base58.b58encode(compact).decode('utf-8'))

if __name__ == "__main__":
    main()
