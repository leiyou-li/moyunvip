import requests
import re
import time
import json
import random

def get_random_ua():
    # 常用的移动设备 User-Agent 列表
    uas = [
        'Mozilla/5.0 (Linux; Android 12; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36'
    ]
    return random.choice(uas)

def process_m3u():
    # 设置请求头
    headers = {
        'User-Agent': get_random_ua(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'Sec-Ch-Ua-Mobile': '?1',
        'Sec-Ch-Ua-Platform': '"Android"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'Host': 'tv.iill.top',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # 添加 cookies
    cookies = {
        '_ga': 'GA1.1.{}.{}'.format(random.randint(1000000000, 9999999999), random.randint(1000000000, 9999999999)),
        '_ga_XXXXXXXXXXXX': 'GS1.1.{}.1.1.{}.0'.format(int(time.time()), int(time.time())),
    }

    # 尝试获取内容
    url = "https://tv.iill.top/m3u/Gather"
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch content...")
            session = requests.Session()
            
            # 先访问主页
            print("Accessing homepage first...")
            session.get("https://tv.iill.top/", headers=headers, cookies=cookies, timeout=30)
            
            # 添加随机延迟
            time.sleep(random.uniform(1, 3))
            
            # 更新随机 User-Agent
            headers['User-Agent'] = get_random_ua()
            
            # 获取 M3U 内容
            print("Fetching M3U content...")
            response = session.get(
                url,
                headers=headers,
                cookies=cookies,
                timeout=30,
                allow_redirects=True
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 403:
                print("Access forbidden, trying with different parameters...")
                continue
                
            response.raise_for_status()
            content = response.text

            print(f"Content type: {response.headers.get('content-type', 'unknown')}")
            print(f"Content preview: {content[:200]}")

            # 检查是否获取到了正确的 M3U 内容
            if '#EXTM3U' in content:
                print("Found M3U content")
                # 处理内容
                lines = content.split('\n')
                processed_lines = []
                
                # 添加 EPG 源信息到文件开头
                processed_lines.append('#EXTM3U x-tvg-url="https://epg.iill.top/epg"')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith('#EXTINF:'):
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
                    elif not line.startswith('#EXTM3U') and not line.startswith('</'):
                        # 处理 URL 行，排除 HTML 标签
                        if 'http' in line:
                            processed_lines.append(line)
                
                # 保存处理后的内容
                with open('moyun.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(processed_lines))
                
                print("Successfully updated M3U content")
                return
            else:
                print("No valid M3U content found in response")
                print("Full response content:", content)
                raise ValueError("Invalid content received")

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("All attempts failed")
                raise

if __name__ == "__main__":
    process_m3u() 