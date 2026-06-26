import json
import requests
import time
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 配置区 =================

# 1. 核心源（针对大陆全节点 CDN 深度优化、骨干网直连的高速源）
CORE_SITES = [
    {"id": "sn_4k", "name": "💎 索尼·4K顶级采集", "api": "https://suoniapi.com/api.php/provide/vod"},
    {"id": "k4_zy", "name": "🚀 最大·4K特线", "api": "https://api.zuidapi.com/api.php/provide/vod"},
    {"id": "lz_4k", "name": "⚡ 量子·骨干加速", "api": "https://cj.lziapi.com/api.php/provide/vod"},
    {"id": "gs_zy", "name": "🚀 光速·万兆响应", "api": "https://api.guangsuapi.com/api.php/provide/vod"},
    {"id": "yz_hd", "name": "🔥 优质·蓝光/1080P", "api": "https://api.yzzy-api.com/inc/apijson.php/provide/vod"},
    {"id": "fs_zy", "name": "🎬 非凡·全网直连", "api": "https://cj.ffzyapi.com/api.php/provide/vod"},
    {"id": "sd_zy", "name": "📡 闪电·高频宽直连", "api": "https://sdzyapi.com/api.php/provide/vod"},
    {"id": "bf_cdn", "name": "🌪️ 暴风·CDN全节点", "api": "https://bfzyapi.com/api.php/provide/vod"},
    {"id": "yh_dm", "name": "🌸 樱花·动漫专线", "api": "https://m3u8.apiyhzy.com/api.php/provide/vod"},
    {"id": "db_zy", "name": "🎬 豆瓣·高分榜单", "api": "https://caiji.dbzy.tv/api.php/provide/vod"},
    {"id": "mt_zy", "name": "🍶 茅台·精品资源", "api": "https://www.maotaizy.com/api.php/provide/vod/"},
    {"id": "pg_zy", "name": "🍎 苹果·高清专线", "api": "https://api.apilyzy.com/api.php/provide/vod"}
]

# 2. 备选源（保留在大陆有独立直连、CDN 或者加速跳转的有效源，剔除了纯海外极慢节点）
PROVIDED_EXTRA_SITES = [
    {"name": "🎬 爱奇艺资源", "api": "https://iqiyizyapi.com/api.php/provide/vod"},
    {"name": "🎬 豆瓣资源", "api": "https://caiji.dbzy5.com/api.php/provide/vod"},
    {"name": "🎬 茅台资源", "api": "https://caiji.maotaizy.cc/api.php/provide/vod"},
    {"name": "🎬 卧龙资源", "api": "https://wolongzyw.com/api.php/provide/vod"},
    {"name": "🎬 iKun资源", "api": "https://ikunzyapi.com/api.php/provide/vod"},
    {"name": "🎬 电影天堂", "api": "http://caiji.dyttzyapi.com/api.php/provide/vod"},
    {"name": "🎬 猫眼资源", "api": "https://api.maoyanapi.top/api.php/provide/vod"},
    {"name": "🎬 量子资源", "api": "https://cj.lzcaiji.com/api.php/provide/vod"},
    {"name": "🎬 360 资源", "api": "https://360zyzz.com/api.php/provide/vod"},
    {"name": "🎬 极速资源", "api": "https://jszyapi.com/api.php/provide/vod"},
    {"name": "🎬 魔都资源", "api": "https://www.mdzyapi.com/api.php/provide/vod"},
    {"name": "🎬 非凡资源", "api": "https://api.ffzyapi.com/api.php/provide/vod"},
    {"name": "🎬 暴风资源", "api": "https://bfzyapi.com/api.php/provide/vod"},
    {"name": "🎬 最大资源", "api": "https://api.zuidapi.com/api.php/provide/vod"},
    {"name": "🎬 无尽资源", "api": "https://api.wujinapi.me/api.php/provide/vod"},
    {"name": "🎬 新浪资源", "api": "https://api.xinlangapi.com/xinlangapi.php/provide/vod"},
    {"name": "🎬 旺旺资源", "api": "https://api.wwzy.tv/api.php/provide/vod"},
    {"name": "🎬 速播资源", "api": "https://subocaiji.com/api.php/provide/vod"},
    {"name": "🎬 金鹰点播", "api": "https://jinyingzy.com/api.php/provide/vod"},
    {"name": "🎬 光速资源", "api": "https://api.guangsuapi.com/api.php/provide/vod"},
    {"name": "🎬 红牛资源", "api": "https://www.hongniuzy2.com/api.php/provide/vod"},
    {"name": "🎬 魔都动漫", "api": "https://caiji.moduapi.cc/api.php/provide/vod"},
    {"name": "🎬 如意资源", "api": "https://pz.v88.qzz.io/?url=https://cj.rycjapi.com/api.php/provide/vod"},
    {"name": "🎬 豪华资源", "api": "https://pz.v88.qzz.io/?url=https://hhzyapi.com/api.php/provide/vod"},
    {"name": "🎬 百度云资源", "api": "https://pz.v88.qzz.io/?url=https://api.apibdzy.com/api.php/provide/vod"},
    {"name": "🎬 量子影视", "api": "https://cj.lziapi.com/api.php/provide/vod"},
    {"name": "🎬 最大点播", "api": "https://zuidazy.me/api.php/provide/vod"},
    {"name": "🎬 无尽影视", "api": "https://api.wujinapi.com/api.php/provide/vod"},
    {"name": "🎬 旺旺短剧", "api": "https://wwzy.tv/api.php/provide/vod"},
    {"name": "🎬 虎牙资源", "api": "https://www.huyaapi.com/api.php/provide/vod"},
    {"name": "🎬 快车资源", "api": "https://caiji.kuaichezy.org/api.php/provide/vod"},
    {"name": "🎬 闪电资源", "api": "https://xsd.sdzyapi.com/api.php/provide/vod"},
    # --- 18+ 分类（精选在大陆直连和加载表现较好的源） ---
    {"name": "🔞 麻豆视频", "api": "https://91md.me/api.php/provide/vod"},
    {"name": "🔞 玉兔资源", "api": "https://apiyutu.com/api.php/provide/vod"},
    {"name": "🔞 老色逼", "api": "https://apilsbzy1.com/api.php/provide/vod"},
    {"name": "🔞 优优资源", "api": "https://www.yytv4.cc/api.php/provide/vod"},
    {"name": "🔞 小鸡资源", "api": "https://api.xiaojizy.live/provide/vod"},
    {"name": "🔞 黄色仓库", "api": "https://hsckzy.xyz/api.php/provide/vod"},
    {"name": "🔞 大奶子", "api": "https://apidanaizi.com/api.php/provide/vod"},
    {"name": "🔞 jkun资源", "api": "https://jkunzyapi.com/api.php/provide/vod"},
    {"name": "🔞 辣椒资源", "api": "https://pz.v88.qzz.io/?url=https://apilj.com/api.php/provide/vod"},
    {"name": "🔞 鲨鱼资源", "api": "https://shayuapi.com/api.php/provide/vod"},
    {"name": "🔞 豆豆资源", "api": "https://api.douapi.cc/api.php/provide/vod"},
    {"name": "🔞 黑料资源", "api": "https://www.heiliaozyapi.com/api.php/provide/vod"},
    {"name": "🔞 百万资源", "api": "https://api.bwzyz.com/api.php/provide/vod"},
    {"name": "🔞 桃花资源", "api": "https://thzy1.me/api.php/provide/vod"},
    {"name": "🔞 精品资源", "api": "https://www.jingpinx.com/api.php/provide/vod"},
    {"name": "🔞 CK资源", "api": "https://ckzy.me/api.php/provide/vod"},
    {"name": "🔞 细胞资源", "api": "https://www.xxibaozyw.com/api.php/provide/vod"},
    {"name": "🔞 香蕉资源", "api": "https://www.xiangjiaozyw.com/api.php/provide/vod"},
    {"name": "🔞 美少女", "api": "https://www.msnii.com/api/json.php"},
    {"name": "🔞 杏吧资源", "api": "https://xingba222.com/api.php/provide/vod"},
    {"name": "🔞 色猫资源", "api": "https://caiji.semaozy.net/inc/apijson_vod.php/provide/vod"}
]

CRAWL_SOURCES = [
    "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/jingjian.txt"
]

OUTPUT_FILE = "deco.json"
OUTPUT_TXT_FILE = "deco_b58.txt"

# 核心优化：调低超时阀值。大陆直连握手如果超过 6 秒，代表实际播片肯定会卡顿，直接在测速阶段舍弃。
TIMEOUT = 6        
MAX_WORKERS = 30   
TARGET_TOTAL = 36  

# ================= Base58 内置核心加密模块 =================

B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def base58_encode(raw_bytes: bytes) -> str:
    n = int.from_bytes(raw_bytes, byteorder="big")
    result = ""
    while n > 0:
        n, remainder = divmod(n, 58)
        result = B58_ALPHABET[remainder] + result
    for b in raw_bytes:
        if b == 0:
            result = B58_ALPHABET[0] + result
        else:
            break
    return result

# ================= 逻辑处理区 =================

def fetch_external_apis():
    print("🌐 正在刮擦指定的精简文本源...")
    collected = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    for url in CRAWL_SOURCES:
        try:
            r = requests.get(url, timeout=6, verify=False, headers=headers)
            if r.status_code != 200: continue
            
            links = re.findall(r'https?://[^\s"\'\[\]\u4e00-\u9fa5]+', r.text)
            for link in links:
                if any(x in link for x in ["/api.php", "provide/vod", "/api/json", "apijson", "/feifei"]):
                    clean_link = link.replace("\\/", "/").rstrip(",;\"'")
                    collected.add(clean_link)
        except Exception:
            continue
    return list(collected)

def verify_and_speed_test(api_info):
    api_url = api_info["api"]
    try:
        test_url = f"{api_url}?ac=list" if "?" not in api_url else f"{api_url}&ac=list"
        start_time = time.time()
        # 模拟大陆常见浏览器 User-Agent，部分大厂采集站会拦截无 UA 请求
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(test_url, timeout=TIMEOUT, verify=False, headers=headers)
        latency = (time.time() - start_time) * 1000  
        
        if r.status_code == 200:
            return {
                "valid": True,
                "api": api_url,
                "name": api_info["name"],
                "is_core": api_info["is_core"],
                "latency": latency
            }
    except Exception:
        pass
    return {"valid": False, "api": api_url}

def check_and_build():
    start_time = time.time()
    all_tasks = []
    added_apis = set()
    
    # 1. 加载大陆核心特线源
    for site in CORE_SITES:
        if site["api"] not in added_apis:
            all_tasks.append({"api": site["api"], "name": site["name"], "is_core": True})
            added_apis.add(site["api"])
            
    # 2. 加载全量备选直连源
    for site in PROVIDED_EXTRA_SITES:
        if site["api"] not in added_apis:
            all_tasks.append({"api": site["api"], "name": site["name"], "is_core": False})
            added_apis.add(site["api"])
        
    # 3. 解析刮擦源
    try:
        external_links = fetch_external_apis()
        fresh_links = [l for l in external_links if l not in added_apis]
        for idx, link in enumerate(fresh_links):
            all_tasks.append({
                "api": link,
                "name": f"🤖 刮擦精简源_{idx+1:02d}",
                "is_core": False
            })
    except Exception:
        pass
        
    print(f"🔎 整合完毕，开始在大陆优化模式下并发测速（排除高延迟/卡顿源）...")
    
    valid_nodes = []
    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_node = {executor.submit(verify_and_speed_test, task): task for task in all_tasks}
            for future in as_completed(future_to_node):
                try:
                    res = future.result()
                    if res and res.get("valid"):
                        valid_nodes.append(res)
                except Exception:
                    pass
    except Exception:
        pass

    # 4. 速度（响应延迟）绝对优先排序
    valid_nodes.sort(key=lambda x: x.get("latency", 99999))
    
    # 5. 精选截取速度最高的大陆直连前 36 个优质节点
    valid_api_site = {}
    final_nodes = valid_nodes[:TARGET_TOTAL]
    
    for i, node in enumerate(final_nodes):
        try:
            speed_prefix = f"⚡[{int(node['latency'])}ms] " if i < 10 else ""
            if node["is_core"]:
                display_name = f"{speed_prefix}{node['name']}"
                site_id = f"core_{i}"
            else:
                clean_name = node["name"] if "刮擦精简源" not in node["name"] else f"精简源_{i+1:02d}"
                display_name = f"{speed_prefix}{clean_name}"
                site_id = f"auto_{i}"
                
            valid_api_site[site_id] = {
                "api": node["api"],
                "name": display_name,
                "detail": node["api"].split("/api.php")[0] if "/api.php" in node["api"] else node["api"]
            }
        except Exception:
            continue

    # 组装符合规范的完整 JSON 对象
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

    # 6. 文件生成与全量完美 JSON 结构 Base58 转换
    try:
        # 先保存明文的 JSON 数据留底
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)
        
        # 将结构完全相同的 JSON 格式直接进行全量 Base58 转换
        json_string_content = json.dumps(final_json, ensure_ascii=False)
        encoded_bytes = json_string_content.encode("utf-8")
        b58_encrypted_string = base58_encode(encoded_bytes)
        
        # 写入完美的 Base58 密文文件
        with open(OUTPUT_TXT_FILE, "w", encoding="utf-8") as f:
            f.write(b58_encrypted_string)
            
        print(f"🚀 【大陆加速优化完成】最快的前 {len(final_nodes)} 个全网极速直连源已完成 Base58 编码，成功推送到 {OUTPUT_TXT_FILE}")
            
    except Exception as e:
        print(f"❌ 最终保存写入失败: {e}")

if __name__ == "__main__":
    check_and_build()
