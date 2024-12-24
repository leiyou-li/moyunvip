import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

def fetch_and_decrypt():
    # 获取源数据
    url = "https://tv.iill.top/m3u/Gather"
    try:
        print("正在获取数据...")
        response = requests.get(url)
        data = response.text
        print(f"获取到的数据长度: {len(data)}")
        print(f"数据预览: {data[:200]}...")  # 显示前200个字符
        
        # 将数据写入文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            f.write(data)
            
        print("成功获取数据")
        
        # 验证文件是否写入成功
        if os.path.exists('output.txt'):
            with open('output.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"\n文件大小: {os.path.getsize('output.txt')} 字节")
            print(f"文件内容预览: {content[:200]}...")
        else:
            print("警告：文件未创建成功")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    fetch_and_decrypt() 