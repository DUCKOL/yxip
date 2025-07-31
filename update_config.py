import json
import random

# ================= 配置区 =================

# 内置的域名列表 (代替ip.txt)
# 使用 set 去重，确保每个域名只出现一次，然后转回 list
DOMAIN_LIST = list(set([
    "russia.com",
    "visa.ca",
    "visa.co.in",
    "www.csgo.com",
    "japan.com",
    "malaysia.com"
]))

# V2Ray配置文件路径
CONFIG_FILE_PATH = 'config.json' 

# =========================================

def update_v2ray_config(config_path, address_list):
    """
    读取V2Ray配置，用列表中的地址随机更新节点的'address'字段，然后保存。
    """
    if not address_list:
        print("错误：地址列表为空，无法更新配置。")
        return

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        print(f"成功读取配置文件: {config_path}")
    except FileNotFoundError:
        print(f"错误：配置文件 {config_path} 未找到。请确保该文件存在于仓库根目录。")
        return
    except json.JSONDecodeError:
        print(f"错误：配置文件 {config_path} 格式不正确，不是有效的JSON。")
        return

    # 核心逻辑：遍历outbounds并随机替换地址
    if 'outbounds' in config_data and isinstance(config_data['outbounds'], list):
        updated_nodes_count = 0
        for outbound in config_data['outbounds']:
            # 检查节点是否是vless/vmess等常见类型，它们通常有vnext设置
            if (outbound.get('settings') and 
                isinstance(outbound['settings'].get('vnext'), list) and 
                outbound['settings']['vnext']):
                
                # 从您的域名列表中随机选择一个
                random_address = random.choice(address_list)
                
                # 更新地址
                old_address = outbound['settings']['vnext'][0].get('address', 'N/A')
                outbound['settings']['vnext'][0]['address'] = random_address
                
                print(f"节点地址已更新: {old_address} -> {random_address}")
                updated_nodes_count += 1
        
        if updated_nodes_count == 0:
            print("警告：在配置文件中没有找到符合条件的可更新节点。")
            return

    else:
        print("警告：在配置文件中没有找到 'outbounds' 列表，无法进行更新。")
        return

    # 将修改后的配置写回文件
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            # indent=2 使JSON文件格式优美，易于阅读
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print(f"成功更新配置文件并保存到 {config_path}。")
    except Exception as e:
        print(f"错误：写入配置文件时发生错误。错误详情：{e}")


if __name__ == '__main__':
    print("开始使用内置域名列表更新配置文件...")
    # 检查域名列表是否为空
    if DOMAIN_LIST:
        update_v2ray_config(CONFIG_FILE_PATH, DOMAIN_LIST)
    else:
        print("错误：内置域名列表为空，已跳过更新步骤。")
