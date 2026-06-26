import json
import requests
import time
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 全自动搜刮配置 =================

# 1. 仅保留最核心的大厂骨干直连作为保底（极少改动且速度极快）
CORE_SITES = [
    {"id": "sn_4k", "name": "💎 索尼·4K顶级采集", "api": "https://suoniapi.com/api.php/provide/vod"},
    {"id": "k4_zy", "name": "🚀 最大·4K特线", "api": "https://api.zuidapi.com/api.php/provide/vod"},
    {"id": "lz_4k", "name": "⚡ 量子·骨干加速", "api": "https://cj.lziapi.com/api.php/provide/vod"},
    {"id": "gs_zy", "name": "🚀 光速·万兆响应", "api": "https://api.guangsuapi.com/api.php/provide/vod"}
]

# 2. 全网自动搜刮源订阅池（脚本会自动抓取并解析这些地址里的所有隐藏接口）
CRAWL_SOURCES = [
    "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/jingjian.txt",
    "https://raw.githubusercontent.com/FongMi/CatVodSpider/main/json/config.json",
    "https://raw.githubusercontent.com/yydsys/yydsys/main/yydsys.json",
    "https://mirror.ghproxy.com/https://raw.githubusercontent.com/gaotianliuyun/0707/main/X.json"
]

OUTPUT_FILE = "deco.json"
OUTPUT_TXT_FILE = "deco_b58.txt"

# 严格限制大陆直连延迟。全自动搜刮来的接口，握手超过 4 秒的直接扔掉，确保筛选出的都是极速源
TIMEOUT = 4        
MAX_WORKERS = 40   
TARGET_TOTAL = 36  

# ================= Base58 核心模块 =================

B58_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def base58_encode(raw_bytes: bytes) -> str:
    """高负载安全的标准 Base58 编码"""
    try:
        n = int.from_bytes(raw_bytes, byteorder="big")
        result = bytearray()
        while n > 0:
            n, remainder = divmod(n, 58)
            result.append(B58_ALPHABET[remainder])
        for b in raw_bytes:
            if b == 0:
                result.append(B58_ALPHABET[0])
            else:
                break
        result.reverse()
        return result.decode("ascii")
    except Exception:
        num = int(''.join([f'{b:02x}' for b in raw_bytes]), 16)
        res = ''
        while num > 0:
            num, rem = divmod(num, 58)
            res = chr(B58_ALPHABET[rem]) + res
        return res

# ================= 全自动网络搜刮逻辑 =================

def dynamic_crawl_all_apis():
    """动态全网搜刮接口逻辑"""
    print("🌐 开始从订阅池全自动搜刮、挖掘最新接口...")
    collected_apis = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for url in CRAWL_SOURCES:
        try:
            r = requests.get(url, timeout=8, verify=False, headers=headers)
            if r.status_code != 200: continue
            
            text_data = r.text
            
            # 模式 1：从标准的 JSON 配置结构中抽取 api 地址
            if "{" in text_data and "}" in text_data:
                try:
                    js = json.loads(text_data)
                    # 递归寻找疑似视频采集站的 api
                    def find_apis(obj):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                if k in ["api", "url"] and isinstance(v, str) and "http" in v:
                                    if any(x in v for x in ["/api.php", "provide/vod", "/api/json", "apijson", "/feifei"]):
                                        collected_apis.add(v.strip())
                                else:
                                    find_apis(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                find_apis(item)
                    find_apis(js)
                except Exception:
                    pass
            
            # 模式 2：通用的正则表达式兜底搜刮（不论文本、纯文本、海报网还是魔改配置，全量挖掘 URL）
            links = re.findall(r'https?://[^\s"\'\[\]\u4e00-\u9fa5]+', text_data)
            for link in links:
                # 过滤出符合各大影视站 CMS 的接口特征短语
                if any(x in link for x in ["/api.php", "provide/vod", "/api/json", "apijson", "/feifei"]):
                    clean_link = link.replace("\\/", "/").rstrip(",;\"'}")
                    collected_apis.add(clean_link)
        except Exception:
            continue
            
    print(f"📥 搜刮完毕！共挖掘到 {len(collected_apis)} 个备选动态源。")
    return list(collected_apis)

def verify_and_speed_test(api_url, is_core=False, index=0):
    """多线程并发测速与大陆有效性验证"""
    try:
        test_url = f"{api_url}?ac=list" if "?" not in api_url else f"{api_url}&ac=list"
        start_time = time.time()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(test_url, timeout=TIMEOUT, verify=False, headers=headers)
        latency = (time.time() - start_time) * 1000  
        
        if r.status_code == 200:
            # 判定名字
            if is_core:
                name = [x["name"] for x in CORE_SITES if x["api"] == api_url][0]
            else:
                name = f"🎬 自动搜刮源_{index+1:02d}"
                
            return {
                "valid": True,
                "api": api_url,
                "name": name,
                "is_core": is_core,
                "latency": latency
            }
    except Exception:
        pass
    return {"valid": False, "api": api_url}

def check_and_build():
    all_tasks = []
    added_apis = set()
    
    # 1. 注入绝对稳定的核心保底源
    for site in CORE_SITES:
        if site["api"] not in added_apis:
            all_tasks.append({"api": site["api"], "is_core": True, "index": 0})
            added_apis.add(site["api"])
            
    # 2. 获取动态自动搜刮出来的海量全网源并注入
    scraped_links = dynamic_crawl_all_apis()
    for idx, link in enumerate(scraped_links):
        if link not in added_apis:
            all_tasks.append({"api": link, "is_core": False, "index": idx})
            added_apis.add(link)
        
    print(f"⚡ 开始对全网 {len(all_tasks)} 个采集源进行多线程高并发测速...")
    
    valid_nodes = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_node = {executor.submit(verify_and_speed_test, task["api"], task["is_core"], task["index"]): task for task in all_tasks}
        for future in as_completed(future_to_node):
            res = future.result()
            if res and res.get("valid"):
                valid_nodes.append(res)

    # 3. 速度绝对优先排序（延迟低的排在最前面，卡顿的被超时机制直接扔掉）
    valid_nodes.sort(key=lambda x: x.get("latency", 99999))
    
    # 4. 截取最快、最畅通的前 36 个优质接口
    valid_api_site = {}
    final_nodes = valid_nodes[:TARGET_TOTAL]
    
    for i, node in enumerate(final_nodes):
        try:
            speed_prefix = f"⚡[{int(node['latency'])}ms] " if i < 10 else ""
            if node["is_core"]:
                display_name = f"{speed_prefix}{node['name']}"
                site_id = f"core_{i}"
            else:
                display_name = f"{speed_prefix}{node['name']}"
                site_id = f"auto_{i}"
                
            valid_api_site[site_id] = {
                "api": node["api"],
                "name": display_name,
                "detail": node["api"].split("/api.php")[0] if "/api.php" in node["api"] else node["api"]
            }
        except Exception:
            continue

    # 5. 组装完美的标准规范 JSON 结构
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

    # 6. 保存留底 JSON 并对其全量转化为 Base58 密文流
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)
        
        # 转化成紧凑型纯 JSON 字符串
        json_string_content = json.dumps(final_json, ensure_ascii=False)
        encoded_bytes = json_string_content.encode("utf-8")
        
        # 实施安全 Base58 编码
        b58_encrypted_string = base58_encode(encoded_bytes)
        
        # 写入密文文件
        with open(OUTPUT_TXT_FILE, "w", encoding="utf-8") as f:
            f.write(b58_encrypted_string)
            
        print(f"🎉【完美搜刮并加密】已自动挑选出全网延迟最低的 {len(final_nodes)} 个节点，成功写入 {OUTPUT_TXT_FILE}")
            
    except Exception as e:
        print(f"❌ 最终保存写入失败: {e}")

if __name__ == "__main__":
    check_and_build()
