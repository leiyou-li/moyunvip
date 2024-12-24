import requests
import re
import time
import json
import random

def get_random_ua():
    # 常用的移动设备 User-Agent 列表
    uas = [
        'okhttp/3.12.0',  # TVBOX 常用的 UA
        'okhttp/4.9.0',
        'Dalvik/2.1.0',
        'TVBOX/1.0.0',
        'XiaoMi/MiuiBrowser/13.5.40'
    ]
    return random.choice(uas)

def process_m3u():
    # 设置请求头
    headers = {
        'User-Agent': get_random_ua(),
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'Keep-Alive',
        'Host': 'tv.iill.top'
    }

    # 尝试不同的 URL 格式
    urls = [
        "https://tv.iill.top/m3u/Gather",
        "@https://tv.iill.top/m3u/Gather",  # 尝试带 @ 符号的格式
        "https://tv.iill.top/m3u/Gather?type=m3u",
        "https://tv.iill.top/m3u/Gather?_=" + str(int(time.time() * 1000))  # 添加时间戳
    ]

    max_retries = 3
    retry_delay = 5

    for url in urls:
        print(f"\nTrying URL: {url}")
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} to fetch content...")
                session = requests.Session()
                
                # 获取 M3U 内容
                response = session.get(
                    url.lstrip('@'),  # 移除可能的 @ 符号
                    headers=headers,
                    timeout=30,
                    verify=False  # 禁用 SSL 验证
                )
                
                print(f"Response status code: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 403:
                    print("Access forbidden, trying next URL or attempt...")
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
                    continue

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                continue

    print("All URLs and attempts failed")
    raise Exception("Failed to fetch M3U content")

if __name__ == "__main__":
    # 禁用 SSL 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    process_m3u() 