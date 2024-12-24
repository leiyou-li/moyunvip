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

def convert_m3u_to_txt(m3u_file, txt_file):
    """将M3U文件转换为分类格式的TXT文件"""
    try:
        # 读取M3U文件
        with open(m3u_file, 'r', encoding='utf-8') as f:
            m3u_content = f.read()
            
        print(f"M3U文件大小: {os.path.getsize(m3u_file)} 字节")
        
        # 解析M3U内容
        lines = m3u_content.split('\n')
        channels = {}
        current_name = None
        current_resolution = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#EXTINF:'):
                # 从 #EXTINF 行提取频道名称
                try:
                    # 提取频道名称和分辨率
                    info = line.split(',', 1)[1]
                    if '[' in info and ']' in info:
                        name_part = info.split('[')[0]
                        resolution = info[info.find('[')+1:info.find(']')]
                        current_name = name_part.strip()
                        current_resolution = resolution
                    else:
                        current_name = info.strip()
                        current_resolution = "1920*1080"  # 默认分辨率
                except:
                    current_name = None
                    current_resolution = None
            elif not line.startswith('#') and current_name:
                # 这是URL行
                category = "央视高清"  # 默认分类
                if current_name and "CCTV" in current_name:
                    if category not in channels:
                        channels[category] = []
                    entry = f"{current_name}[{current_resolution}],{line}"
                    channels[category].append(entry)
                current_name = None
                current_resolution = None
        
        # 写入TXT文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            # 写入分类和频道
            for category, entries in channels.items():
                f.write(f"{category},#genre#\n")
                f.write('\n'.join(entries))
                f.write('\n\n')
                
        print(f"成功转换并保存到: {txt_file}")
        return True
        
    except Exception as e:
        print(f"转换过程中发生错误: {str(e)}")
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
        
        # 转换为分类格式
        print("\n开始转换为分类格式...")
        if not convert_m3u_to_txt('output.txt', 'moyun.txt'):
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