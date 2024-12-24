import requests
import re
import time
import json

def process_m3u():
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Host': 'tv.iill.top'
    }

    # 尝试获取内容
    url = "https://tv.iill.top/m3u/Gather"
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch content...")
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            content = response.text

            print(f"Response status code: {response.status_code}")
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