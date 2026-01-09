import json
import requests
import time

# ================= 配置区 =================
# 核心源列表：仅保留万兆/4K/CDN重型节点
# 延迟高没关系，只要出口带宽大
TARGET_SITES = [
    {"id": "sn_4k", "name": "💎 索尼·4K顶级采集", "api": "https://suoniapi.com/api.php/provide/vod"},
    {"id": "k4_zy", "name": "🚀 最大·4K特线", "api": "https://api.zuidapi.com/api.php/provide/vod"},
    {"id": "lz_4k", "name": "⚡ 量子·骨干加速", "api": "https://cj.lziapi.com/api.php/provide/vod"},
    {"id": "gs_zy", "name": "🚀 光速·万兆响应", "api": "https://api.guangsuapi.com/api.php/provide/vod"},
    {"id": "yz_hd", "name": "🔥 优质·蓝光/1080P", "api": "https://api.yzzy-api.com/inc/apijson.php/provide/vod"},
    {"id": "sd_zy", "name": "📡 闪电·高频宽直连", "api": "https://sdzyapi.com/api.php/provide/vod"},
    {"id": "bf_cdn", "name": "🌪️ 暴风·CDN全节点", "api": "https://bfzyapi.com/api.php/provide/vod"},
    {"id": "yh_dm", "name": "🌸 樱花·动漫专线", "api": "https://m3u8.apiyhzy.com/api.php/provide/vod"},
    {"id": "db_zy", "name": "🎬 豆瓣·高分榜单", "api": "https://caiji.dbzy.tv/api.php/provide/vod"}
]

OUTPUT_FILE = "deco.json"
# 这里的超时设为 15s，确保重型服务器握手不超时
TIMEOUT = 15 

# ================= 逻辑区 =================

def check_and_build():
    valid_api_site = {}
    
    print(f"开始探测重型源 (超时限制: {TIMEOUT}s)...")
    
    for site in TARGET_SITES:
        try:
            start = time.time()
            # 增加 verify=False 避免某些证书过期的重型源报错
            resp = requests.get(site["api"], timeout=TIMEOUT, verify=False)
            duration = time.time() - start
            
            if resp.status_code == 200:
                print(f"✅ {site['name']} | 状态: 正常 | 延迟: {duration:.2f}s")
                # 构造 DecoTV 专用 API 节点格式
                valid_api_site[site["id"]] = {
                    "api": site["api"],
                    "name": site["name"],
                    "detail": site["api"].split("/api.php")[0]
                }
            else:
                print(f"⚠️ {site['name']} 返回状态码: {resp.status_code}")
        except Exception as e:
            print(f"❌ {site['name']} 探测失败: 离线或响应过慢")

    # 构建 DecoTV/LunaTV 嵌套 JSON 结构
    final_json = {
        "cache_time": 9200,
        "api_site": valid_api_site,
        "custom_category": [
            {"name": "🎞️ 4K·高码率重型区", "type": "movie", "query": "4K"},
            {"name": "🍿 Netflix·专区", "type": "movie", "query": "网飞"},
            {"name": "🧧 华语·年度精选", "type": "movie", "query": "华语"},
            {"name": "🍱 2026·动漫新番", "type": "anime", "query": "2026"}
        ]
    }

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)
    
    print(f"\n✨ 更新完成！符合 DecoTV 格式的库已写入 {OUTPUT_FILE}")

if __name__ == "__main__":
    check_and_build()
