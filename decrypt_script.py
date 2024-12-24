import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 导入解密脚本
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
        response = requests.get(url)
        encrypted_data = response.text
        print(f"获取到的加密数据长度: {len(encrypted_data)}")
        print(f"加密数据预览: {encrypted_data[:200]}...")
        
        # 使用解密服务进行解密
        print("\n开始解密数据...")
        decrypted_data = decrypt_url(encrypted_data)  # 传递加密的内容而不是URL
        print(f"解密结果类型: {type(decrypted_data)}")
        
        # 检查解密结果
        if decrypted_data is None:
            print("解密失败，返回结果为空")
            return
            
        # 如果解密结果是字典或列表，转换为字符串
        if isinstance(decrypted_data, (dict, list)):
            print("解密结果是字典或列表，转换为字符串...")
            decrypted_data = json.dumps(decrypted_data, ensure_ascii=False, indent=2)
        elif not isinstance(decrypted_data, str):
            print(f"解密结果是其他类型: {type(decrypted_data)}，尝试转换为字符串...")
            decrypted_data = str(decrypted_data)
        
        print(f"\n解密后数据长度: {len(str(decrypted_data))}")
        print(f"解密后数据预览: {str(decrypted_data)[:200]}...")
        
        # 将解密后的数据写入文件
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("\n正在写入文件...")
        
        try:
            with open('output.m3u', 'w', encoding='utf-8') as f:
                f.write(f"# 更新时间：{timestamp}\n\n")
                f.write(str(decrypted_data))
            print("文件写入完成")
        except Exception as e:
            print(f"文件写入失败: {str(e)}")
            raise
            
        print("成功获取并解密数据")
        
        # 验证文件是否写入成功
        if os.path.exists('output.m3u'):
            with open('output.m3u', 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"\n文件大小: {os.path.getsize('output.m3u')} 字节")
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