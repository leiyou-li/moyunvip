import requests
import re
import time
import json
import random

def get_tvbox_headers():
    """获取 TVBOX 专用请求头"""
    return {
        'User-Agent': 'okhttp/3.12.0',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip',
        'Connection': 'keep-alive',
        'Host': 'tv.iill.top',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

def process_m3u():
    session = requests.Session()
    
    # 使用 TVBOX 专用请求头
    headers = get_tvbox_headers()
    
    # 直接请求 M3U 地址
    url = "https://tv.iill.top/m3u/Gather"
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch content...")
            
            # 模拟 TVBOX 的请求方式
            response = session.get(
                url,
                headers=headers,
                timeout=30,
                verify=False,  # 禁用 SSL 验证
                allow_redirects=True,  # 允许重定向
                stream=True  # 使用流式传输
            )
            
            # 设置正确的编码
            response.encoding = 'utf-8'
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"Error status code: {response.status_code}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                continue

            # 读取内容
            content = response.text
            print(f"Content preview: {content[:200]}")

            # 检查是否获取到了正确的 M3U 内容
            if '#EXTM3U' in content:
                print("Found M3U content")
                # 处理内容
                lines = content.split('\n')
                processed_lines = []
                
                # 添加 EPG 源信息到文件开头
                processed_lines.append('#EXTM3U x-tvg-url="https://epg.iill.top/epg"')
                
                # 标记是否在处理频道信息
                is_channel_info = False
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith('#EXTINF:'):
                        is_channel_info = True
                        # 处理频道信息行
                        group_match = re.search(r'group-title="([^"]*)"', line)
                        group_title = group_match.group(1) if group_match else "IPTV"
                        
                        channel_name = re.search(r',(.+)$', line)
                        if channel_name:
                            name = channel_name.group(1).strip()
                            if 'tvg-id="' not in line:
                                line = line.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-id="{name}"')
                            if 'tvg-name="' not in line:
                                line = line.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-name="{name}"')
                        processed_lines.append(line)
                    elif is_channel_info and line.startswith('http'):
                        # 这是频道 URL
                        processed_lines.append(line)
                        is_channel_info = False
                
                # 保存处理后的内容
                with open('moyun.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(processed_lines))
                
                print("Successfully updated M3U content")
                print(f"Processed {len(processed_lines)} lines")
                return
            else:
                print("No valid M3U content found in response")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                continue

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            continue

    print("All attempts failed")
    raise Exception("Failed to fetch M3U content")

if __name__ == "__main__":
    # 禁用 SSL 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    process_m3u() 