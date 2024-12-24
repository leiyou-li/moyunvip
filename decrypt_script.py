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

def convert_m3u_to_txt(m3u_content):
    """将M3U格式转换为TXT格式"""
    lines = m3u_content.split('\n')
    txt_lines = []
    current_name = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#EXTINF:'):
            # 从 #EXTINF 行提取频道名称
            try:
                current_name = line.split(',', 1)[1]
            except:
                current_name = None
        elif not line.startswith('#'):
            # 这是一个URL行
            if current_name:
                txt_lines.append(f"{current_name},{line}")
            else:
                txt_lines.append(line)
            current_name = None
    
    return '\n'.join(txt_lines)

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
        print(f"解密后数据预览: {str(decrypted_data)[:200]}...")
        
        # 将解密后的数据写入M3U文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            f.write(str(decrypted_data))
            
        print("成功解密数据并保存为M3U格式")
        
        # 转换为TXT格式
        print("\n开始转换为TXT格式...")
        txt_content = convert_m3u_to_txt(str(decrypted_data))
        
        # 保存TXT文件
        with open('moyun.txt', 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            f.write(txt_content)
            
        print("成功转换并保存为TXT格式")
        
        # 验证文件是否写入成功
        if os.path.exists('moyun.txt'):
            with open('moyun.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"\nTXT文件大小: {os.path.getsize('moyun.txt')} 字节")
            print(f"TXT文件内容预览: {content[:200]}...")
        else:
            print("警告：TXT文件未创建成功")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    fetch_and_decrypt()