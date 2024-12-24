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
        
        # 将解密后的数据写入文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(f"# 更新时间：{timestamp}\n\n")
            f.write(str(decrypted_data))
            
        print("成功解密数据")
        
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