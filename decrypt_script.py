import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 打印当前工作目录和文件列表
print("当前工作目录:", os.getcwd())
print("目录内容:", os.listdir())
print("url-decrypt-service 目录内容:", os.listdir('./url-decrypt-service'))

# 添加子模块到 Python 路径
module_path = os.path.abspath('./url-decrypt-service')
sys.path.insert(0, module_path)
print("Python 路径:", sys.path)

try:
    from 接口解密脚本 import decrypt_url
except ImportError as e:
    print(f"导入错误详情: {str(e)}")
    print("Error: 无法导入解密模块，请确保子模块已正确克隆")
    sys.exit(1)

def fetch_and_decrypt():
    # 获取源数据
    url = "https://tv.iill.top/m3u/Gather"
    try:
        response = requests.get(url)
        encrypted_data = response.text
        
        # 使用解密服务进行解密
        decrypted_data = decrypt_url(encrypted_data)
        
        # 将解密后的数据写入文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            f.write(decrypted_data)
            
        print("成功获取并解密数据")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    fetch_and_decrypt() 