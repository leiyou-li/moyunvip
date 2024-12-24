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
    """将M3U文件转换为TXT文件"""
    print("\n开始从M3U文件读取内容...")
    
    try:
        # 读取M3U文件
        with open(m3u_file, 'r', encoding='utf-8') as f:
            m3u_content = f.read()
            
        print(f"M3U文件大小: {os.path.getsize(m3u_file)} 字节")
        print(f"M3U内容预览: {m3u_content[:500]}...")
        
        lines = m3u_content.split('\n')
        print(f"总行数: {len(lines)}")
        
        txt_lines = []
        current_name = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#EXTINF:'):
                # 从 #EXTINF 行提取频道名称
                try:
                    current_name = line.split(',', 1)[1]
                    print(f"找到频道名称: {current_name}")
                except:
                    current_name = None
                    print(f"无法从行提取频道名称: {line}")
            elif not line.startswith('#'):
                # 这是一个URL行
                if current_name:
                    entry = f"{current_name},{line}"
                    txt_lines.append(entry)
                    print(f"添加条目: {entry}")
                else:
                    txt_lines.append(line)
                    print(f"添加URL (无名称): {line}")
                current_name = None
        
        print(f"\n转换完成，共生成 {len(txt_lines)} 个条目")
        result = '\n'.join(txt_lines)
        
        # 保存TXT文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            f.write(result)
            
        print(f"成功保存到TXT文件: {txt_file}")
        print(f"TXT文件大小: {os.path.getsize(txt_file)} 字节")
        print(f"TXT内容预览: {result[:500]}...")
        
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
        print(f"解密后数据预览: {str(decrypted_data)[:200]}...")
        
        # 将解密后的数据写入M3U文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            f.write(str(decrypted_data))
            
        print("成功解密数据并保存为M3U格式")
        
        # 转换M3U文件为TXT格式
        print("\n开始转换M3U文件为TXT格式...")
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