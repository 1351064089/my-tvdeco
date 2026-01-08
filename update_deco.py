import json, base58

def main():
    # 经过 2026 年验证的顶级高速 CMS 接口（涵盖量子、非凡、华策、索尼等大厂）
    # 这些源在国内电视端起播极快
    premium_list = [
        {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "🔥量子高清4K"},
        {"api": "https://cj.ffzyapi.com/api.php/provide/vod", "name": "🔥非凡秒开"},
        {"api": "https://cj.huaceapi.com/api.php/provide/vod", "name": "华策极清"},
        {"api": "https://video.gture.top/api.php/provide/vod", "name": "光速蓝光"},
        {"api": "https://bfzyapi.com/api.php/provide/vod", "name": "暴风高清"},
        {"api": "https://api.kkzy.tv/api.php/provide/vod", "name": "快看资源"},
        {"api": "https://www.feisuzyapi.com/api.php/provide/vod", "name": "飞速资源"},
        {"api": "https://jszyapi.com/api.php/provide/vod", "name": "极速资源"},
        {"api": "https://api.tianyiapi.com/api.php/provide/vod", "name": "天翼影视"},
        {"api": "https://snzypm.com/api.php/provide/vod", "name": "索尼资源"},
        {"api": "https://www.605zy.cc/api.php/provide/vod", "name": "605大片"},
        {"api": "https://subocaiji.com/api.php/provide/vod", "name": "速播影音"},
        {"api": "https://cj.sdzyapi.com/api.php/provide/vod", "name": "闪电资源"},
        {"api": "https://www.kuaichezy.com/api.php/provide/vod", "name": "快车资源"},
        {"api": "https://api.123zy.com/api.php/provide/vod", "name": "123酷享"}
        # 此处在生成的 JSON 中会自动循环补齐至 50 个，确保 DecoTV 索引满载
    ]

    # 自动补齐逻辑：如果精选源不够 50 个，则循环增加索引，确保 50 个位置不留空
    final_50 = []
    while len(final_50) < 50:
        base_site = premium_list[len(final_50) % len(premium_list)]
        site_copy = base_site.copy()
        # 给重复的站点加编号，防止 DecoTV 解析冲突
        if len(final_50) >= len(premium_list):
            site_copy['name'] = f"{base_site['name']}(备)"
        final_50.append(site_copy)

    # 完善 detail 字段
    for s in final_50:
        s['detail'] = s['api'].split("api.php")[0]

    config = {
        "cache_time": 9200,
        "api_site": {f"site_{i:02d}": s for i, s in enumerate(final_50)},
        "custom_category": [
            {"name": "🎞️ 115·蓝光专区", "type": "movie", "query": "115"},
            {"name": "🔥 4K·极清", "type": "movie", "query": "4K"},
            {"name": "🌸 2026新番", "type": "anime", "query": "2026"},
            {"name": "📺 华语精选", "type": "movie", "query": "华语"}
        ]
    }

    # 写入 JSON 文件
    with open("deco.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # 写入 Base58 编码文件
    compact_json = json.dumps(config, ensure_ascii=False).encode('utf-8')
    b58_text = base58.b58encode(compact_json).decode('utf-8')
    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(b58_text)

if __name__ == "__main__":
    main()
