import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 导入解密模块
try:
    from 接口解密脚本 import decrypt_url
except ImportError as e:
    print(f"导入错误详情: {str(e)}")
    print("Error: 无法导入解密模块")
    sys.exit(1)

def load_channel_config(config_file):
    """加载频道配置"""
    categories = {}
    current_category = None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                if line.endswith('#genre#'):
                    current_category = line.replace(',#genre#', '')
                    categories[current_category] = []
                elif current_category:
                    categories[current_category].append(line)
                    
        return categories
    except Exception as e:
        print(f"加载配置文件出错: {str(e)}")
        return None

def convert_m3u_to_txt(m3u_file, txt_file, channel_config):
    """将M3U文件按配置转换为TXT文件"""
    try:
        # 读取M3U文件
        with open(m3u_file, 'r', encoding='utf-8') as f:
            m3u_content = f.read()
            
        print(f"M3U文件大小: {os.path.getsize(m3u_file)} 字节")
        print("开始解析频道信息...")
        
        # 解析M3U内容
        lines = m3u_content.split('\n')
        channels = {category: [] for category in channel_config.keys()}
        current_name = None
        current_resolution = None
        current_url = None
        
        # 创建频道名称到分类的映射
        channel_to_category = {}
        for category, channel_list in channel_config.items():
            for channel in channel_list:
                channel_to_category[channel.lower()] = (category, channel)  # 保存原始名称
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#EXTINF:'):
                # 从 #EXTINF 行提取频道名称
                try:
                    info = line.split(',', 1)[1]
                    name_part = info
                    resolution = "1920*1080"  # 默认分辨率
                    
                    if '[' in info and ']' in info:
                        name_part = info.split('[')[0].strip()
                        resolution = info[info.find('[')+1:info.find(']')]
                    
                    # 规范化名称进行匹配
                    name_part = name_part.lower().replace('高清', '').replace('HD', '').strip()
                    print(f"处理频道: {name_part}")
                    
                    # 查找匹配的频道名称
                    for config_name in channel_to_category:
                        if config_name.lower() in name_part:
                            category, original_name = channel_to_category[config_name]
                            current_name = original_name
                            current_resolution = resolution
                            print(f"找到匹配: {original_name} -> {category}")
                            break
                except Exception as e:
                    print(f"处理频道名称时出错: {str(e)}")
                    current_name = None
                    current_resolution = None
                    
            elif not line.startswith('#') and current_name:
                # 这是URL行
                category = channel_to_category.get(current_name.lower())[0]
                if category:
                    entry = f"{current_name}[{current_resolution}],{line}"
                    channels[category].append(entry)
                    print(f"添加频道: {entry}")
                current_name = None
                current_resolution = None
        
        # 写入TXT文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            # 按配置文件的顺序写入分类和频道
            for category, channel_list in channel_config.items():
                if channels[category]:  # 只写入有内容的分类
                    f.write(f"{category},#genre#\n")
                    f.write('\n'.join(channels[category]))
                    f.write('\n\n')
                    print(f"写入分类 {category}: {len(channels[category])} 个频道")
                
        print(f"成功转换并保存到: {txt_file}")
        return True
        
    except Exception as e:
        print(f"转换过程中发生错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return False

def fetch_and_decrypt():
    # 要解密的URL
    url = "https://tv.iill.top/m3u/Gather"
    try:
        print("开始解密数据...")
        decrypted_data = decrypt_url(url)
        
        if decrypted_data is None:
            print("解密失败，返回结果为空")
            return
            
        print(f"解密后数据长度: {len(str(decrypted_data))}")
        
        # 将解密后的数据写入M3U文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            f.write(str(decrypted_data))
            
        print("成功解密数据并保存为M3U格式")
        
        # 加载频道配置
        print("\n加载频道配置...")
        channel_config = load_channel_config('channel_config.txt')
        if not channel_config:
            print("警告：无法加载频道配置")
            return
            
        # 转换为分类格式
        print("\n开始按配置转换为分类格式...")
        if not convert_m3u_to_txt('output.txt', 'moyun.txt', channel_config):
            print("警告：转换失败")
            return
            
        print("所有操作完成")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    fetch_and_decrypt()
    fetch_and_decrypt()