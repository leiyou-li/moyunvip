import requests
import json
import time
import logging
import re
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """验证URL格式是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def decrypt_url(encrypted_url, max_retries=3, timeout=10):
    """解密URL的函数"""
    if not is_valid_url(encrypted_url):
        logger.error("无效的URL格式")
        return None

    url = "https://api.lige.chat/ua"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'origin': 'https://lige.chat',
        'referer': 'https://lige.chat/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    payload = {"url": encrypted_url}

    for attempt in range(max_retries):
        try:
            logger.info(f"尝试第 {attempt + 1} 次解密...")
            logger.debug(f"发送请求: {url}")
            logger.debug(f"请求数据: {payload}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            logger.debug(f"状态码: {response.status_code}")
            logger.debug(f"响应头: {dict(response.headers)}")
            
            response.raise_for_status()
            
            if not response.text.strip():
                raise ValueError("收到空响应")
                
            # 尝试解析JSON响应
            try:
                result = response.json()
                return json.dumps(result, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                return response.text
                
        except requests.exceptions.Timeout:
            logger.error(f"请求超时")
            if attempt == max_retries - 1:
                return None
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                logger.error(f"{max_retries}次尝试后失败: {e}")
                return None
            logger.warning(f"第{attempt + 1}次尝试失败: {e}")
            logger.info("1秒后重试...")
            time.sleep(1)
        except Exception as e:
            logger.error(f"意外错误: {e}")
            return None

def main():
    logger.info("URL解密工具启动")
    print("\n欢迎使用URL解密工具！")
    print("输入 'q' 退出程序")
    
    while True:
        try:
            encrypted_url = input("\n请输入需要解密的URL: ").strip()
            if encrypted_url.lower() == 'q':
                print("感谢使用，再见！")
                break
                
            if not encrypted_url:
                print("URL不能为空，请重试")
                continue
                
            result = decrypt_url(encrypted_url)
            if result:
                print("\n解密结果:")
                print(result)
            else:
                print("\n解密失败，请检查URL是否正确")
                
            print("\n" + "-"*50)
            
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            break
        except Exception as e:
            logger.error(f"程序运行错误: {e}")
            print("发生错误，请重试")

if __name__ == "__main__":
    main() 