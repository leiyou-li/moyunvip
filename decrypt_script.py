import requests
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

def fetch_and_decrypt():
    # 获取源数据
    url = "https://tv.iill.top/m3u/Gather"
    try:
        print("正在获取数据...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        encrypted_data = response.text
        print(f"获取到的加密数据长度: {len(encrypted_data)}")
        print(f"加密数据预览: {encrypted_data[:200]}...")
        
        # 使用解密服务进行解密
        print("\n开始解密数据...")
        decrypted_data = decrypt_url(encrypted_data)
        
        if decrypted_data is None:
            print("解密失败，返回结果为空")
            return
            
        print(f"解密后数据长度: {len(str(decrypted_data))}")
        print(f"解密后数据预览: {str(decrypted_data)[:200]}...")
        
        # 将解密后的数据写入文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            f.write(str(decrypted_data))
            
        print("成功获取并解密数据")
        
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