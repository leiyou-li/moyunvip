import requests
import re
import time
import json

def get_lige_headers():
    """获取 lige.chat 使用的请求头"""
    return {
        'authority': 'tv.iill.top',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'if-modified-since': 'Thu, 01 Jan 1970 00:00:00 GMT',
        'if-none-match': 'W/"65a64e51-135f"',
        'sec-ch-ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
    }

def process_m3u():
    session = requests.Session()
    headers = get_lige_headers()
    
    url = "https://tv.iill.top/m3u/Gather"
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch content...")
            
            # 先访问主页建立 session
            print("Accessing homepage first...")
            session.get("https://tv.iill.top/", headers=headers, verify=False)
            
            # 添加延迟模拟真实访问
            time.sleep(2)
            
            # 获取 M3U 内容
            print("Fetching M3U content...")
            response = session.get(
                url,
                headers=headers,
                verify=False,
                allow_redirects=True
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                content = response.text
                print(f"Content preview: {content[:200]}")

                if '#EXTM3U' in content:
                    print("Found M3U content")
                    lines = content.split('\n')
                    processed_lines = []
                    
                    # 添加 EPG 源信息到文件开头
                    processed_lines.append('#EXTM3U x-tvg-url="https://epg.iill.top/epg"')
                    
                    current_group = None
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        if line.startswith('#EXTINF:'):
                            # 处理频道信息行
                            group_match = re.search(r'group-title="([^"]*)"', line)
                            if group_match:
                                current_group = group_match.group(1)
                            else:
                                current_group = "IPTV"
                                line = line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{current_group}"')
                            
                            channel_name = re.search(r',(.+)$', line)
                            if channel_name:
                                name = channel_name.group(1).strip()
                                if 'tvg-id="' not in line:
                                    line = line.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-id="{name}"')
                                if 'tvg-name="' not in line:
                                    line = line.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-name="{name}"')
                            processed_lines.append(line)
                        elif line.startswith('http'):
                            # 这是频道 URL
                            processed_lines.append(line)
                    
                    # 保存处理后的内容
                    with open('moyun.txt', 'w', encoding='utf-8') as f:
                        f.write('\n'.join(processed_lines))
                    
                    print("Successfully updated M3U content")
                    print(f"Processed {len(processed_lines)} lines")
                    return
            
            print(f"Attempt {attempt + 1} failed")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            continue

    print("All attempts failed")
    raise Exception("Failed to fetch M3U content")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    process_m3u() 