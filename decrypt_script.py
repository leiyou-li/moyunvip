import json
import sys
import os
from datetime import datetime
from pathlib import Path
import re

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
        
        # 打印前几行内容用于调试
        print("\nM3U文件内容预览:")
        preview_lines = m3u_content.split('\n')[:10]
        for line in preview_lines:
            print(line)
            
        # 解析M3U内容
        lines = m3u_content.split('\n')
        channels = {}
        for category in channel_config.keys():
            channels[category] = {}  # 使用字典而不是列表
        
        current_name = None
        current_resolution = None
        
        # 创建频道名称到分类的映射
        channel_to_category = {}
        for category, channel_list in channel_config.items():
            for channel in channel_list:
                # 处理配置中的频道名称，移除特殊字符
                clean_name = channel.lower().replace('-', '').replace('综合', '')\
                    .replace('财经', '').replace('少儿', '')\
                    .replace('体育', '').replace('电影', '')\
                    .replace('音乐', '').replace('新闻', '')
                channel_to_category[clean_name] = (category, channel)
                print(f"配置频道映射: {clean_name} -> {channel}")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#EXTINF:'):
                try:
                    # 打印完整的 EXTINF 行用于调试
                    print(f"\n处理EXTINF行: {line}")
                    
                    # 尝试不同的属性模式
                    tvg_name = None
                    
                    # 尝试 tvg-name 属性
                    tvg_name_match = re.search(r'tvg-name="([^"]+)"', line)
                    if tvg_name_match:
                        tvg_name = tvg_name_match.group(1)
                        print(f"找到 tvg-name: {tvg_name}")
                    
                    # 尝试 group-title 属性
                    group_match = re.search(r'group-title="([^"]+)"', line)
                    if group_match:
                        group_title = group_match.group(1)
                        print(f"找到 group-title: {group_title}")
                    
                    # 尝试逗号后的名称
                    name_parts = line.split(',')
                    if len(name_parts) > 1:
                        comma_name = name_parts[1].strip()
                        print(f"找到逗号后名称: {comma_name}")
                    
                    if tvg_name:
                        clean_tvg_name = tvg_name.lower().replace('-', '').replace('hd', '')\
                            .replace('高清', '').strip()
                        
                        # 获取分辨率
                        resolution = "1920*1080"  # 默认分辨率
                        if '[' in line and ']' in line:
                            resolution = line[line.find('[')+1:line.find(']')]
                        
                        # 查找匹配的频道名称
                        for config_name, (category, original_name) in channel_to_category.items():
                            if config_name in clean_tvg_name or clean_tvg_name in config_name:
                                current_name = original_name
                                current_resolution = resolution
                                print(f"找到匹配: {tvg_name} -> {original_name} ({category})")
                                break
                except Exception as e:
                    print(f"处理频道名称时出错: {str(e)}")
                    current_name = None
                    current_resolution = None
                    
            elif not line.startswith('#') and current_name:
                # 这是URL行
                try:
                    category = channel_to_category[current_name.lower().replace('-', '')][0]
                    if category:
                        # 如果频道不存在，创建一个新列表
                        if current_name not in channels[category]:
                            channels[category][current_name] = []
                        # 添加新的URL条目，不包含分辨率信息
                        entry = f"{current_name},{line}"  # 直接使用频道名和URL
                        channels[category][current_name].append(entry)
                        print(f"添加频道: {entry}")
                except Exception as e:
                    print(f"添加频道条目时出错: {str(e)}")
                current_name = None
                current_resolution = None
        
        # 写入TXT文件
        with open(txt_file, 'w', encoding='utf-8') as f:
            # 写入更新日期
            timestamp = datetime.now().strftime("%Y-%m-%d")
            f.write(f"墨韵更新日期,#genre#\n")
            f.write(f"{timestamp},https://gitlab.com/lr77/IPTV/-/raw/main/%E8%B5%B7%E9%A3%8E%E4%BA%86.mp4\n\n")
            
            # 按配置文件的顺序写入分类和频道
            for category, channel_list in channel_config.items():
                if channels[category]:  # 只写入有内容的分类
                    f.write(f"💮{category},#genre#\n")  # 添加emoji
                    # 按照配置文件中的顺序遍历频道
                    for channel_name in channel_list:
                        if channel_name in channels[category]:
                            # 写入该频道的所有URL
                            urls = channels[category][channel_name]
                            for entry in urls:
                                f.write(entry + '\n')  # 直接写入，因为格式已经正确
                    f.write('\n')
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
            f.write(f"墨韵更新,#genre#\n\n")  # 修改为新的格式
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