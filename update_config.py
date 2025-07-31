import requests
from bs4 import BeautifulSoup
import re
import os
import json
import random

# ================= 配置区 =================

# 目标URL列表，用于抓取IP
URLS_TO_SCRAPE = [
    'https://api.uouin.com/cloudflare.html', 
    'https://ip.164746.xyz'
]

# V2Ray配置文件路径
CONFIG_FILE_PATH = 'config.json' 

# =========================================

def scrape_ips(urls):
    """从给定的URL列表中抓取IP地址。"""
    print("开始从URL抓取IP地址...")
    ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    collected_ips = []
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 如果请求失败则抛出异常
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有可能包含IP的'tr'标签
            elements = soup.find_all('tr')
            for element in elements:
                ip_matches = re.findall(ip_pattern, element.get_text())
                if ip_matches:
                    collected_ips.extend(ip_matches)
        except requests.RequestException as e:
            print(f"警告：无法从 {url} 抓取内容。错误：{e}")
            
    # 去重并返回
    unique_ips = sorted(list(set(collected_ips)))
    print(f"成功抓取到 {len(unique_ips)} 个唯一IP地址。")
    return unique_ips

def update_v2ray_config(config_path, ip_list):
    """读取V2Ray配置，随机更新节点的地址，然后保存。"""
    if not ip_list:
        print("错误：IP地址列表为空，无法更新配置。")
        return

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        print(f"成功读取配置文件: {config_path}")
    except FileNotFoundError:
        print(f"错误：配置文件 {config_path} 未找到。请确保该文件存在。")
        return
    except json.JSONDecodeError:
        print(f"错误：配置文件 {config_path} 格式不正确。")
        return

    # 核心逻辑：遍历outbounds并随机替换地址
    # V2Ray/Xray的标准结构中，地址通常在 outbounds -> settings -> vnext -> address
    if 'outbounds' in config_data and isinstance(config_data['outbounds'], list):
        updated_nodes = 0
        for outbound in config_data['outbounds']:
            # 确保路径存在
            if (outbound.get('settings') and 
                isinstance(outbound['settings'].get('vnext'), list) and 
                outbound['settings']['vnext']):
                
                # 随机选择一个IP
                random_ip = random.choice(ip_list)
                
                # 更新地址
                old_address = outbound['settings']['vnext'][0].get('address', 'N/A')
                outbound['settings']['vnext'][0]['address'] = random_ip
                print(f"节点地址更新：{old_address} -> {random_ip}")
                updated_nodes += 1
        
        if updated_nodes == 0:
            print("警告：在配置文件中没有找到可更新的节点。")
            return

    else:
        print("警告：在配置文件中没有找到 'outbounds' 列表。")
        return

    # 将修改后的配置写回文件
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print(f"成功更新配置文件并保存到 {config_path}。")
    except Exception as e:
        print(f"错误：无法写入配置文件。错误：{e}")


if __name__ == '__main__':
    # 1. 抓取IP
    available_ips = scrape_ips(URLS_TO_SCRAPE)
    
    # 2. 如果成功抓取到IP，则更新配置文件
    if available_ips:
        update_v2ray_config(CONFIG_FILE_PATH, available_ips)
    else:
        print("由于未能抓取到任何IP，跳过配置文件更新步骤。")
