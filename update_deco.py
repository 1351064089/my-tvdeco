import json
import requests
import time
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 配置区 =================

# 1. 核心源：升级为包含“云盘/海外专线”的重型节点
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

# 2. 全量备选解析源（保留所有常规影视和 18+ 特殊分类，完全不剥离）
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
    {"name": "🎬 飘零资源", "api": "https://p2100.net/api.php/provide/vod"},
    {"name": "🎬 U酷影视", "api": "https://api.ukuapi88.com/api.php/provide/vod"},
    {"name": "🎬 光速资源", "api": "https://api.guangsuapi.com/api.php/provide/vod"},
    {"name": "🎬 红牛资源", "api": "https://www.hongniuzy2.com/api.php/provide/vod"},
    {"name": "🎬 魔都动漫", "api": "https://caiji.moduapi.cc/api.php/provide/vod"},
    {"name": "🎬 如意资源", "api": "https://pz.v88.qzz.io/?url=https://cj.rycjapi.com/api.php/provide/vod"},
    {"name": "🎬 豪华资源", "api": "https://pz.v88.qzz.io/?url=https://hhzyapi.com/api.php/provide/vod"},
    {"name": "🎬 百度云资源", "api": "https://pz.v88.qzz.io/?url=https://api.apibdzy.com/api.php/provide/vod"},
    {"name": "🎬 艾旦影视", "api": "https://pz.v88.qzz.io/?url=https://lovedan.net/api.php/provide/vod"},
    {"name": "🎬 量子影视", "api": "https://cj.lziapi.com/api.php/provide/vod"},
    {"name": "🎬 最大点播", "api": "https://zuidazy.me/api.php/provide/vod"},
    {"name": "🎬 无尽影视", "api": "https://api.wujinapi.com/api.php/provide/vod"},
    {"name": "🎬 旺旺短剧", "api": "https://wwzy.tv/api.php/provide/vod"},
    {"name": "🎬 虎牙资源", "api": "https://www.huyaapi.com/api.php/provide/vod"},
    {"name": "🎬 鸭鸭资源", "api": "https://cj.yayazy.net/api.php/provide/vod"},
    {"name": "🎬 快车资源", "api": "https://caiji.kuaichezy.org/api.php/provide/vod"},
    {"name": "🎬 闪电资源", "api": "https://xsd.sdzyapi.com/api.php/provide/vod"},
    # --- 成人(18+) 分类资源并入测速序列 ---
    {"name": "🔞 麻豆视频", "api": "https://91md.me/api.php/provide/vod"},
    {"name": "🔞 AIvin", "api": "http://lbapiby.com/api.php/provide/vod"},
    {"name": "🔞 155资源", "api": "https://155api.com/api.php/provide/vod"},
    {"name": "🔞 玉兔资源", "api": "https://apiyutu.com/api.php/provide/vod"},
    {"name": "🔞 番号资源", "api": "http://fhapi9.com/api.php/provide/vod"},
    {"name": "🔞 老色逼", "api": "https://apilsbzy1.com/api.php/provide/vod"},
    {"name": "🔞 优优资源", "api": "https://www.yytv4.cc/api.php/provide/vod"},
    {"name": "🔞 小鸡资源", "api": "https://api.xiaojizy.live/provide/vod"},
    {"name": "🔞 黄色仓库", "api": "https://hsckzy.xyz/api.php/provide/vod"},
    {"name": "🔞 大奶子", "api": "https://apidanaizi.com/api.php/provide/vod"},
    {"name": "🔞 jkun资源", "api": "https://jkunzyapi.com/api.php/provide/vod"},
    {"name": "🔞 乐播资源", "api": "https://lbapi9.com/api.php/provide/vod"},
    {"name": "🔞 奶香资源", "api": "https://Naixxzy.com/api.php/provide/vod"},
    {"name": "🔞 森林资源", "api": "https://beiyong.slapibf.com/api.php/provide/vod"},
    {"name": "🔞 辣椒资源", "api": "https://pz.v88.qzz.io/?url=https://apilj.com/api.php/provide/vod"},
    {"name": "🔞 鲨鱼资源", "api": "https://shayuapi.com/api.php/provide/vod"},
    {"name": "🔞 豆豆资源", "api": "https://api.douapi.cc/api.php/provide/vod"},
    {"name": "🔞 滴滴资源", "api": "https://api.ddapi.cc/api.php/provide/vod"},
    {"name": "🔞 黑料资源", "api": "https://www.heiliaozyapi.com/api.php/provide/vod"},
    {"name": "🔞 百万资源", "api": "https://api.bwzyz.com/api.php/provide/vod"},
    {"name": "🔞 桃花资源", "api": "https://thzy1.me/api.php/provide/vod"},
    {"name": "🔞 精品资源", "api": "https://www.jingpinx.com/api.php/provide/vod"},
    {"name": "🔞 CK资源", "api": "https://ckzy.me/api.php/provide/vod"},
    {"name": "🔞 souavZY", "api": "https://api.souavzyw.net/api.php/provide/vod"},
    {"name": "🔞 细胞资源", "api": "https://www.xxibaozyw.com/api.php/provide/vod"},
    {"name": "🔞 香蕉资源", "api": "https://www.xiangjiaozyw.com/api.php/provide/vod"},
    {"name": "🔞 美少女", "api": "https://www.msnii.com/api/json.php"},
    {"name": "🔞 黄AVZY", "api": "https://www.pgxdy.com/api/json.php"},
    {"name": "🔞 白嫖资源", "api": "https://www.kxgav.com/api/json.php"},
    {"name": "🔞 杏吧资源", "api": "https://xingba222.com/api.php/provide/vod"},
    {"name": "🔞 大地资源", "api": "https://dadiapi.com/feifei"},
    {"name": "🔞 色猫资源", "api": "https://caiji.semaozy.net/inc/apijson_vod.php/provide/vod"},
    {"name": "🔞 奥斯卡", "api": "https://aosikazy.com/api.php/provide/vod"},
    {"name": "🔞 丝袜资源", "api": "https://siwazyw.tv/api.php/provide/vod"}
]

# 3. 指定刮擦的目标文本地址
CRAWL_SOURCES = [
    "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/jingjian.txt"
]

OUTPUT_FILE = "deco.json"
OUTPUT_TXT_FILE = "deco_b58.txt"
TIMEOUT = 12       # 超时设置
MAX_WORKERS = 30   # 并发线程数
TARGET_TOTAL = 36  # 目标保留的总节点数

# ================= 逻辑区 =================

def fetch_external_apis():
    """定向刮擦指定文本地址中的全部合法影视接口（不进行剥离）"""
    print("🌐 正在刮擦指定的精简文本源（全量保留，包含18+）...")
    collected = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    for url in CRAWL_SOURCES:
        try:
            r = requests.get(url, timeout=10, verify=False, headers=headers)
            if r.status_code != 200: continue
            
            # 增强正则：精确匹配包含 api.php、provide/vod、api/json 的各种连接
            links = re.findall(r'https?://[^\s"\'\[\]\u4e00-\u9fa5]+', r.text)
            for link in links:
                if "/api.php" in link or "provide/vod" in link or "/api/json" in link or "apijson" in link:
                    # 清洗链接中的多余转义符和尾部特殊标点
                    clean_link = link.replace("\\/", "/").rstrip(",;\"'")
                    collected.add(clean_link)
        except Exception:
            continue
    return list(collected)

def verify_and_speed_test(api_info):
    """测试接口存活状态并记录响应延迟(毫秒)"""
    api_url = api_info["api"]
    try:
        test_url = f"{api_url}?ac=list" if "?" not in api_url else f"{api_url}&ac=list"
        start_time = time.time()
        r = requests.get(test_url, timeout=TIMEOUT, verify=False)
        latency = (time.time() - start_time) * 1000  # 转换为毫秒
        
        if r.status_code == 200 and ("list" in r.text or "vod" in r.text or "code" in r.text or "page" in r.text):
            return {
                "valid": True,
                "api": api_url,
                "name": api_info["name"],
                "is_core": api_info["is_core"],
                "latency": latency
            }
    except:
        pass
    return {"valid": False, "api": api_url}

def check_and_build():
    start_time = time.time()
    all_tasks = []
    added_apis = set()
    
    # 1. 归集核心源
    for site in CORE_SITES:
        if site["api"] not in added_apis:
            all_tasks.append({
                "api": site["api"],
                "name": site["name"],
                "is_core": True
            })
            added_apis.add(site["api"])
            
    # 2. 归集预设优质源
    for site in PROVIDED_EXTRA_SITES:
        if site["api"] not in added_apis:
            all_tasks.append({
                "api": site["api"],
                "name": site["name"],
                "is_core": False
            })
            added_apis.add(site["api"])
        
    # 3. 刮擦目标文本中的所有新接口
    external_links = fetch_external_apis()
    fresh_links = [l for l in external_links if l not in added_apis]
    
    for idx, link in enumerate(fresh_links):
        all_tasks.append({
            "api": link,
            "name": f"🤖 刮擦精简源_{idx+1:02d}",
            "is_core": False
        })
        
    print(f"🔎 整合完毕：队列内包含 {len(added_apis)} 个预设源，从目标文本新挖出 {len(fresh_links)} 个潜在接口。")
    print(f"⚡ 开始进行高并发测速排序...")
    
    valid_nodes = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_node = {executor.submit(verify_and_speed_test, task): task for task in all_tasks}
        for future in as_completed(future_to_node):
            res = future.result()
            if res["valid"]:
                valid_nodes.append(res)

    # 4. 速度优先：升序排序
    valid_nodes.sort(key=lambda x: x["latency"])
    
    # 5. 截取前 36 个
    valid_api_site = {}
    final_nodes = valid_nodes[:TARGET_TOTAL]
    
    for i, node in enumerate(final_nodes):
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

    # 6. 构造 JSON 规范
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

    # 7. 写入 JSON 文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)
    
    # 8. 同步写入文本格式的 deco_b58.txt 供外链读取
    with open(OUTPUT_TXT_FILE, "w", encoding="utf-8") as f:
        for key in valid_api_site:
            f.write(f"{valid_api_site[key]['api']}\n")
    
    end_time = time.time()
    print(f"\n✨ 更新完成！总用时: {int(end_time - start_time)} 秒")
    print(f"📊 共筛选出 {len(valid_nodes)} 个有效源。")
    print(f"🚀 {OUTPUT_FILE} 与 {OUTPUT_TXT_FILE} 已经同步写入并排序完成。")

if __name__ == "__main__":
    check_and_build()
