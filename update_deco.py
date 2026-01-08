import json, base58

def main():
    # 精选全网 50 个完全不同域名的独立接口
    # 哪怕你的运营商封锁了其中一半，剩下的 25 个也足够你用了
    source_pool = [
        {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "💎量子4K"},
        {"api": "https://api.ffzyapi.com/api.php/provide/vod", "name": "💎非凡影视"},
        {"api": "https://jszyapi.com/api.php/provide/vod", "name": "💎极速资源"},
        {"api": "https://api.guangsuapi.com/api.php/provide/vod", "name": "💎光速蓝光"},
        {"api": "https://suoniapi.com/api.php/provide/vod", "name": "💎索尼资源"},
        {"api": "https://bfzyapi.com/api.php/provide/vod", "name": "💎暴风高清"},
        {"api": "https://hhzyapi.com/api.php/provide/vod", "name": "💎豪华资源"},
        {"api": "https://api.1080zyku.com/inc/api_mac10.php", "name": "💎1080P库"},
        {"api": "https://api.kkzy.tv/api.php/provide/vod", "name": "💎快看资源"},
        {"api": "https://snzypm.com/api.php/provide/vod", "name": "💎索尼PM"},
        {"api": "https://www.feisuzyapi.com/api.php/provide/vod", "name": "💎飞速资源"},
        {"api": "https://api.tianyiapi.com/api.php/provide/vod", "name": "💎天翼影视"},
        {"api": "https://subocaiji.com/api.php/provide/vod", "name": "💎速播资源"},
        {"api": "https://cj.sdzyapi.com/api.php/provide/vod", "name": "💎闪电资源"},
        {"api": "https://api.123zy.com/api.php/provide/vod", "name": "💎123资源"},
        {"api": "https://jinyingzy.com/api.php/provide/vod", "name": "💎金鹰资源"},
        {"api": "https://cj.yayazy.net/api.php/provide/vod", "name": "💎鸭鸭资源"},
        {"api": "https://api.xinlangapi.com/xinlangapi.php/provide/vod", "name": "💎新浪资源"},
        {"api": "https://www.605zy.cc/api.php/provide/vod", "name": "💎605资源"},
        {"api": "https://ikunzyapi.com/api.php/provide/vod", "name": "💎IKUN资源"},
        {"api": "https://api.yzzy-api.com/inc/ldg_api_all.php", "name": "💎优质资源"},
        {"api": "https://www.huyaapi.com/api.php/provide/vod", "name": "💎虎牙资源"},
        {"api": "https://dbzy.tv/api.php/provide/vod", "name": "💎豆瓣资源"},
        {"api": "https://www.mdzyapi.com/api.php/provide/vod", "name": "💎魔都资源"},
        {"api": "https://caiji.moduapi.cc/api.php/provide/vod", "name": "💎魔都动漫"},
        {"api": "https://api.wujinapi.me/api.php/provide/vod", "name": "💎无尽资源"},
        {"api": "https://www.kuaichezy.com/api.php/provide/vod", "name": "💎快车资源"},
        {"api": "https://api.apibdzy.com/api.php/provide/vod", "name": "💎百度资源"},
        {"api": "https://www.hongniuzy2.com/api.php/provide/vod", "name": "💎红牛资源"},
        {"api": "https://caiji.maotaizy.cc/api.php/provide/vod", "name": "💎茅台资源"},
        {"api": "https://m3u8.apiyhzy.com/api.php/provide/vod", "name": "💎樱花资源"},
        {"api": "https://api.niuniuzy.me/api.php/provide/vod", "name": "💎牛牛资源"},
        {"api": "https://collect.wolongzyw.com/api.php/provide/vod", "name": "💎卧龙资源"},
        {"api": "https://zy.xmm.hk/api.php/provide/vod", "name": "💎小猫咪源"},
        {"api": "https://tyyszy.com/api.php/provide/vod", "name": "💎天涯资源"},
        {"api": "https://cj.rycjapi.com/api.php/provide/vod", "name": "💎如意资源"},
        {"api": "https://wwzy.tv/api.php/provide/vod", "name": "💎旺旺资源"},
        {"api": "https://api.ukuapi.com/api.php/provide/vod", "name": "💎U酷资源"},
        {"api": "https://www.xxibaozyw.com/api.php/provide/vod", "name": "💎细胞资源"},
        {"api": "https://www.qiqidys.com/api.php/provide/vod/", "name": "💎七七影视"},
        {"api": "https://www.fantuan.tv/api.php/provide/vod/", "name": "💎饭团影视"},
        {"api": "https://json.heimuer.xyz/api.php/provide/vod", "name": "💎黑木耳源"},
        {"api": "https://api.bwzyz.com/api.php/provide/vod", "name": "💎百万资源"},
        {"api": "https://www.mdzyapi.com/api.php/provide/vod", "name": "💎魔都资源"},
        {"api": "https://api.yzzy-api.com/inc/ldg_api_all.php/provide/vod", "name": "💎优质高清"},
        {"api": "https://www.iqiyizyapi.com/api.php/provide/vod", "name": "💎奇艺资源"},
        {"api": "https://p2100.net/api.php/provide/vod", "name": "💎飘零资源"},
        {"api": "https://dadiapi.com/api.php/provide/vod", "name": "💎大地资源"},
        {"api": "https://xsd.sdzyapi.com/api.php/provide/vod", "name": "💎闪电备用"},
        {"api": "https://api.jmzy.com/api.php/provide/vod", "name": "💎金马资源"}
    ]

    final_50 = []
    # 直接填入这 50 个不同的站
    for i, s in enumerate(source_pool):
        item = s.copy()
        item['detail'] = s['api'].split("api.php")[0]
        final_50.append(item)

    config = {
        "cache_time": 9200,
        "api_site": {f"api_{i+1}": s for i, s in enumerate(final_50)},
        "custom_category": [
            {"name": "🎞️ 115·蓝光高清", "type": "movie", "query": "115"},
            {"name": "🔥 4K·极清", "type": "movie", "query": "4K"},
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
