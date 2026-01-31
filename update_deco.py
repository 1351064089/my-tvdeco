import json
import requests
import time
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 配置区 =================

# 1. 核心源：升级为包含“云盘/海外专线”的重型节点
# 针对你提到的《热带夜晚》，我特意增加了对海外资源收录较好的接口
CORE_SITES = [
    {"id": "sn_4k", "name": "💎 索尼·4K顶级采集", "api": "https://suoniapi.com/api.php/provide/vod"},
    {"id": "k4_zy", "name": "🚀 最大·4K特线", "api": "https://api.zuidapi.com/api.php/provide/vod"},
    {"id": "lz_4k", "name": "⚡ 量子·骨干加速", "api": "https://cj.lziapi.com/api.php/provide/vod"},
    {"id": "gs_zy", "name": "🚀 光速·万兆响应", "api": "https://api.guangsuapi.com/api.php/provide/vod"},
    {"id": "yz_hd", "name": "🔥 优质·蓝光/1080P", "api": "https://api.yzzy-api.com/inc/apijson.php/provide/vod"},
    {"id": "fs_zy", "name": "🎬 非凡·海外精选", "api": "https://cj.ffzyapi.com/api.php/provide/vod"},
    {"id": "sd_zy", "name": "📡 闪电·高频宽直连", "api": "https://sdzyapi.com/api.php/provide/vod"},
    {"id": "bf_cdn", "name": "🌪️ 暴风·CDN全节点", "api": "https://bfzyapi.com/api.php/provide/vod"},
    {"id": "yh_dm", "name": "🌸 樱花·动漫专线", "api": "https://m3u8.apiyhzy.com/api.php/provide/vod"},
    {"id": "db_zy", "name": "🎬 豆瓣·高分榜单", "api": "https://caiji.dbzy.tv/api.php/provide/vod"},
    {"id": "mt_zy", "name": "🍶 茅台·精品资源", "api": "https://www.maotaizy.com/api.php/provide/vod/"},
    {"id": "pg_zy", "name": "🍎 苹果·高清专线", "api": "https://api.apilyzy.com/api.php/provide/vod"}
]

# 2. 智能搜集源：扩展了更稳定的仓库地址
CRAWL_SOURCES = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json",
    "https://raw.githubusercontent.com/FongMi/TV/release/lean.json",
    "https://raw.githubusercontent.com/yydsys/yydsys.github.io/master/yydsys.json",
    "http://itvbox.cc/tvbox/meow.json",
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u"
]

OUTPUT_FILE = "deco.json"
TIMEOUT = 12       # 优化超时时间，平衡效率与稳定性
MAX_WORKERS = 30   # 增加并发，全网筛选更快

# ================= 逻辑区 =================

def fetch_external_apis():
    """智能爬取全网接口地址，增加正则兼容性"""
    print("🌐 正在执行全网搜集...")
    collected = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    for url in CRAWL_SOURCES:
        try:
            r = requests.get(url, timeout=10, verify=False, headers=headers)
            if r.status_code != 200: continue
            # 增强正则：匹配标准苹果CMS API以及部分不带vod结尾的变种
            links = re.findall(r'https?://[^\s"\'\[\]]+\/api\.php\/provide\/vod[^\s"\'\[\]]*', r.text)
            for link in links:
                # 清洗链接中的多余转义符
                clean_link = link.replace("\\/", "/")
                collected.add(clean_link)
        except Exception as e:
            continue
    return list(collected)

def verify_api(api_url):
    """测试接口存活状态"""
    try:
        # 增加简易的参数请求测试接口真实有效性
        test_url = f"{api_url}?ac=list" if "?" not in api_url else f"{api_url}&ac=list"
        r = requests.get(test_url, timeout=TIMEOUT, verify=False)
        if r.status_code == 200 and ("list" in r.text or "vod" in r.text or "code" in r.text):
            return api_url
    except:
        return None

def check_and_build():
    valid_api_site = {}
    start_time = time.time()
    
    # --- 步骤 1：处理核心重型源 ---
    print(f"📡 正在验证核心重型源 (万兆/4K/海外专线)...")
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
    print(f"🔎 发现 {len(external_links)} 个潜在接口，开始高并发筛选...")
    
    core_apis = [s["api"] for s in CORE_SITES]
    fresh_links = [l for l in external_links if l not in core_apis]

    # 使用线程池并发验证
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(verify_api, fresh_links))
        
    # 填充有效源，取前30个以保证资源覆盖度
    added_count = 0
    for link in results:
        if link:
            site_id = f"auto_{added_count}"
            # 简单的名称提取逻辑
            valid_api_site[site_id] = {
                "api": link,
                "name": f"🤖 智能源_{added_count+1:02d}",
                "detail": link.split("/api.php")[0]
            }
            added_count += 1
            if added_count >= 30: break

    # --- 步骤 3：构造符合 DecoTV 的嵌套 JSON ---
    final_json = {
        "cache_time": 9200,
        "api_site": valid_api_site,
        "custom_category": [
            {"name": "🎞️ 4K·高码率重型区", "type": "movie", "query": "4K"},
            {"name": "🍿 Netflix·海外精选", "type": "movie", "query": "网飞"},
            {"name": "🧧 华语·年度热映", "type": "movie", "query": "华语"},
            {"name": "🍱 2026·动漫新番", "type": "anime", "query": "2026"},
            {"name": "📺 电视·直播频道", "type": "live", "query": ""}
        ]
    }

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)
    
    end_time = time.time()
    print(f"\n✨ 更新完成！用时: {int(end_time - start_time)}秒")
    print(f"📊 总计保留 {len(valid_api_site)} 个源，已导出至 {OUTPUT_FILE}")

if __name__ == "__main__":
    check_and_build()
