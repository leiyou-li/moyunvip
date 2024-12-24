import requests
import json
import sys
from datetime import datetime
from pathlib import Path

# 添加子模块到 Python 路径
sys.path.append('./url-decrypt-service')

try:
    from 接口解密脚本 import decrypt_url
except ImportError:
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