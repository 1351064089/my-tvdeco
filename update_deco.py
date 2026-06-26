import json
import requests
import time
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 配置区 =================
# (CORE_SITES 和 PROVIDED_EXTRA_SITES 保持不变，确保包含所有资源)
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

CRAWL_SOURCES = ["https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/jingjian.txt"]

# ================= 逻辑区 =================
# (此部分逻辑与你原有代码保持一致，增加了 final_json 和 txt 的同时写入)

def check_and_build():
    # ... (原有合并、测速、排序逻辑) ...
    # 假设这里已经得到了 valid_api_site 这个字典
    
    # 6. 构造 JSON 并同步生成 txt
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

    # 写入 JSON
    with open("deco.json", "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)
    
    # 【新增逻辑】同步写入 deco_b58.txt
    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        for key in valid_api_site:
            f.write(f"{valid_api_site[key]['api']}\n")
    
    print("✅ deco.json 和 deco_b58.txt 已同步更新。")

if __name__ == "__main__":
    check_and_build()
