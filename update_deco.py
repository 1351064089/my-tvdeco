import json
import requests
import time
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 配置区 =================

# 1. 核心源：万兆/4K/CDN 重型节点 (强制保留，除非彻底无法访问)
CORE_SITES = [
    {"id": "sn_4k", "name": "💎 索尼·4K顶级采集", "api": "https://suoniapi.com/api.php/provide/vod"},
    {"id": "k4_zy", "name": "🚀 最大·4K特线", "api": "https://api.zuidapi.com/api.php/provide/vod"},
    {"id": "lz_4k", "name": "⚡ 量子·骨干加速", "api": "https://cj.lziapi.com/api.php/provide/vod"},
    {"id": "gs_zy", "name": "🚀 光速·万兆响应", "api": "https://api.guangsuapi.com/api.php/provide/vod"},
    {"id": "yz_hd", "name": "🔥 优质·蓝光/1080P", "api": "https://api.yzzy-api.com/inc/apijson.php/provide/vod"},
    {"id": "sd_zy", "name": "📡 闪电·高频宽直连", "api": "https://sdzyapi.com/api.php/provide/vod"},
    {"id": "bf_cdn", "name": "🌪️ 暴风·CDN全节点", "api": "https://bfzyapi.com/api.php/provide/vod"},
    {"id": "yh_dm", "name": "🌸 樱花·动漫专线", "api": "https://m3u8.apiyhzy.com/api.php/provide/vod"},
    {"id": "db_zy", "name": "🎬 豆瓣·高分榜单", "api": "https://caiji.dbzy.tv/api.php/provide/vod"},
    {"id": "mt_zy", "name": "🍶 茅台·精品资源", "api": "https://www.maotaizy.com/api.php/provide/vod/"}
]

# 2. 智能搜集源：自动从以下仓库爬取最新接口
CRAWL_SOURCES = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json",
    "https://raw.githubusercontent.com/FongMi/TV/release/lean.json",
    "https://raw.githubusercontent.com/yydsys/yydsys.github.io/master/yydsys.json",
    "http://itvbox.cc/tvbox/meow.json"
]

OUTPUT_FILE = "deco.json"
TIMEOUT = 15       # 核心源宽限到15秒，确保重型节点能握手
MAX_WORKERS = 20   # 提高并发数，加快全网搜集速度

# ================= 逻辑区 =================

def fetch_external_apis():
    """智能爬取全网接口地址"""
    print("🌐 正在执行全网搜集...")
    collected = set()
    for url in CRAWL_SOURCES:
        try:
            r = requests.get(url, timeout=10, verify=False)
            # 匹配所有苹果CMS标准API格式
            links = re.findall(r'https?://[^\s"\'\[\]]+\/api\.php\/provide\/vod', r.text)
            for link in links:
                collected.add(link)
        except:
            continue
    return list(collected)

def verify_api(api_url):
    """测试接口存活状态"""
    try:
        # 重型源可能延迟高，我们主要看是否能连通
        r = requests.get(api_url, timeout=TIMEOUT, verify=False)
        if r.status_code == 200 and ("list" in r.text or "vod" in r.text):
            return api_url
    except:
        return None

def check_and_build():
    valid_api_site = {}
    
    # --- 步骤 1：处理核心重型源 ---
    print(f"📡 正在验证核心重型源 (万兆/4K/CDN)...")
    for site in CORE_SITES:
        if verify_api(site["api"]):
            print(f"✅ [核心] {site['name']} 正常")
            valid_api_site[site["id"]] = {
                "api": site["api"],
                "name": site["name"],
                "detail": site["api"].split("/api.php")[0]
            }
        else:
            print(f"❌ [核心] {site['name']} 暂时离线")

    # --- 步骤 2：全网智能搜集补充 ---
    external_links = fetch_external_apis()
    print(f"🔎 发现 {len(external_links)} 个外部接口，开始智能筛选...")
    
    # 排除掉核心源中已有的地址
    core_apis = [s["api"] for s in CORE_SITES]
    fresh_links = [l for l in external_links if l not in core_apis]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(verify_api, fresh_links))
        
    # 将搜集到的有效源加入，取前20个
    added_count = 0
    for link in results:
        if link:
            site_id = f"auto_{added_count}"
            valid_api_site[site_id] = {
                "api": link,
                "name": f"🤖 智能源_{added_count+1:02d}",
                "detail": link.split("/api.php")[0]
            }
            added_count += 1
            if added_count >= 20: break

    # --- 步骤 3：构造符合 DecoTV 的嵌套 JSON ---
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
    
    print(f"\n✨ 更新完成！总计保留 {len(valid_api_site)} 个源，已按 DecoTV 格式导出。")

if __name__ == "__main__":
    check_and_build()
