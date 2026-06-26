import json
import requests
import time
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 核心配置区 =================

# 1. 核心保底源（根据你提供的那组觉得不错的站点进行全量提取，增加 id 与规范命名）
CORE_SITES = [
    {"id": "dyttzy", "name": "🎬 电影天堂资源", "api": "http://caiji.dyttzyapi.com/api.php/provide/vod"},
    {"id": "ruyi", "name": "🎬 如意资源", "api": "https://cj.rycjapi.com/api.php/provide/vod"},
    {"id": "bfzy", "name": "🎬 暴风资源", "api": "https://bfzyapi.com/api.php/provide/vod"},
    {"id": "tyyszy", "name": "🎬 天涯资源", "api": "https://tyyszy.com/api.php/provide/vod"},
    {"id": "xiaomaomi", "name": "🎬 小猫咪资源", "api": "https://zy.xmm.hk/api.php/provide/vod"},
    {"id": "ffzy", "name": "🎬 非凡影视", "api": "http://ffzy5.tv/api.php/provide/vod"},
    {"id": "heimuer", "name": "🎬 黑木耳资源", "api": "https://json.heimuer.xyz/api.php/provide/vod"},
    {"id": "zy360", "name": "🎬 360资源", "api": "https://360zy.com/api.php/provide/vod"},
    {"id": "iqiyi", "name": "🎬 iqiyi资源", "api": "https://www.iqiyizyapi.com/api.php/provide/vod"},
    {"id": "wolong", "name": "🎬 卧龙资源", "api": "https://wolongzyw.com/api.php/provide/vod"},
    {"id": "hwba", "name": "🎬 华为吧资源", "api": "https://cjhwba.com/api.php/provide/vod"},
    {"id": "jisu", "name": "🎬 极速资源", "api": "https://jszyapi.com/api.php/provide/vod"},
    {"id": "dbzy", "name": "🎬 豆瓣资源", "api": "https://dbzy.tv/api.php/provide/vod"},
    {"id": "mozhua", "name": "🎬 魔爪资源", "api": "https://mozhuazy.com/api.php/provide/vod"},
    {"id": "mdzy", "name": "🎬 魔都资源", "api": "https://www.mdzyapi.com/api.php/provide/vod"},
    {"id": "zuid", "name": "🚀 最大4K特线", "api": "https://api.zuidapi.com/api.php/provide/vod"},
    {"id": "yinghua", "name": "🌸 樱花动漫专线", "api": "https://m3u8.apiyhzy.com/api.php/provide/vod"},
    {"id": "baidu", "name": "🎬 百度云资源", "api": "https://api.apibdzy.com/api.php/provide/vod"},
    {"id": "wujin", "name": "🎬 无尽资源", "api": "https://api.wujinapi.me/api.php/provide/vod"},
    {"id": "wwzy", "name": "🎬 旺旺短剧", "api": "https://wwzy.tv/api.php/provide/vod"},
    {"id": "ikun", "name": "🎬 iKun资源", "api": "https://ikunzyapi.com/api.php/provide/vod"},
    {"id": "lzi", "name": "⚡ 量子骨干加速", "api": "https://cj.lziapi.com/api.php/provide/vod/"}
]

# 2. 全网全自动搜刮订阅源池（自动从以下经典且活跃的配置中无限递归提取隐藏新接口）
CRAWL_SOURCES = [
    "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/jingjian.txt",
    "https://raw.githubusercontent.com/FongMi/CatVodSpider/main/json/config.json",
    "https://raw.githubusercontent.com/yydsys/yydsys/main/yydsys.json",
    "https://mirror.ghproxy.com/https://raw.githubusercontent.com/gaotianliuyun/0707/main/X.json"
]

OUTPUT_FILE = "deco.json"
OUTPUT_TXT_FILE = "deco_b58.txt"

# 针对大陆网络调优：握手或响应超过 4 秒的搜刮源直接扔掉，拒绝播放转圈圈
TIMEOUT = 4        
MAX_WORKERS = 40   
TARGET_TOTAL = 36  

# ================= 健壮型安全 Base58 编码模块 =================

B58_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def base58_encode(raw_bytes: bytes) -> str:
    """工业级防崩溃 Base58 编码，完美应对 GitHub Actions 长文本负载"""
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

# ================= 智能动态搜刮与提取 =================

def dynamic_crawl_all_apis():
    print("🌐 正在全网全自动搜刮、挖掘最新的视频接口...")
    collected_apis = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for url in CRAWL_SOURCES:
        try:
            r = requests.get(url, timeout=8, verify=False, headers=headers)
            if r.status_code != 200: continue
            
            text_data = r.text
            
            # 模式 1：如果检测到是标准的 JSON，递归全量扫描提取
            if "{" in text_data and "}" in text_data:
                try:
                    js = json.loads(text_data)
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
            
            # 模式 2：正则表达式兜底，完美搜刮所有自由文本或混淆订阅格式中的视频 API URL
            links = re.findall(r'https?://[^\s"\'\[\]\u4e00-\u9fa5]+', text_data)
            for link in links:
                if any(x in link for x in ["/api.php", "provide/vod", "/api/json", "apijson", "/feifei"]):
                    clean_link = link.replace("\\/", "/").rstrip(",;\"'}")
                    collected_apis.add(clean_link)
        except Exception:
            continue
            
    print(f"📥 搜刮完成！共动态发掘到 {len(collected_apis)} 个有效采集源。")
    return list(collected_apis)

def verify_and_speed_test(api_url, is_core=False, index=0):
    try:
        test_url = f"{api_url}?ac=list" if "?" not in api_url else f"{api_url}&ac=list"
        start_time = time.time()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(test_url, timeout=TIMEOUT, verify=False, headers=headers)
        latency = (time.time() - start_time) * 1000  
        
        if r.status_code == 200:
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
    
    # 1. 注入你提供觉得不错的核心优质保底源
    for site in CORE_SITES:
        if site["api"] not in added_apis:
            all_tasks.append({"api": site["api"], "is_core": True, "index": 0})
            added_apis.add(site["api"])
            
    # 2. 注入动态全网自动刮擦搜刮出来的最新海量非固定源
    scraped_links = dynamic_crawl_all_apis()
    for idx, link in enumerate(scraped_links):
        if link not in added_apis:
            all_tasks.append({"api": link, "is_core": False, "index": idx})
            added_apis.add(link)
        
    print(f"⚡ 开始对全网 {len(all_tasks)} 个接口进行多线程超高并发测速筛别...")
    
    valid_nodes = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_node = {executor.submit(verify_and_speed_test, task["api"], task["is_core"], task["index"]): task for task in all_tasks}
        for future in as_completed(future_to_node):
            res = future.result()
            if res and res.get("valid"):
                valid_nodes.append(res)

    # 3. 速度绝对优先排序（延迟低的、不卡顿的排在前面）
    valid_nodes.sort(key=lambda x: x.get("latency", 99999))
    
    # 4. 精选截取响应最快的大陆 36 个优质节点
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

    # 5. 组装出与你所需的语法完美一致的标准 JSON 对象
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

    # 6. 保存明文 JSON 并全量转换为 Base58 密文
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)
        
        # 转换整套 JSON 数据为无间隙紧凑型纯文本
        json_string_content = json.dumps(final_json, ensure_ascii=False)
        encoded_bytes = json_string_content.encode("utf-8")
        
        # 安全 Base58 转换
        b58_encrypted_string = base58_encode(encoded_bytes)
        
        # 写入文件
        with open(OUTPUT_TXT_FILE, "w", encoding="utf-8") as f:
            f.write(b58_encrypted_string)
            
        print(f"🎉【动态全自动搜刮完成】成功将延迟最低的 {len(final_nodes)} 个极速直连源注入大结构，并完美加密导出至 {OUTPUT_TXT_FILE}")
            
    except Exception as e:
        print(f"❌ 最终保存写入失败: {e}")

if __name__ == "__main__":
    check_and_build()
