import requests
import re
import time
import json
import base64

def get_tvbox_headers():
    """获取 TVBOX 专用请求头"""
    return {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; M2012K11AC Build/RKQ1.200826.002)',
        'Accept-Encoding': 'gzip',
        'Connection': 'Keep-Alive',
        'Host': 'tv.iill.top'
    }

def process_m3u():
    session = requests.Session()
    headers = get_tvbox_headers()
    
    # TVBOX 配置格式的 URL
    base_url = "https://tv.iill.top/m3u/Gather"
    
    # 尝试不同的编码方式
    urls_to_try = [
        base_url,
        base64.b64encode(base_url.encode()).decode(),  # base64 编码
        f"clan://localhost/{base_url}",  # clan 格式
        f"file://{base_url}",  # file 格式
        f"proxy://do=live&type=txt&ext={base_url}"  # proxy 格式
    ]

    max_retries = 3
    retry_delay = 5

    for url in urls_to_try:
        print(f"\nTrying URL format: {url}")
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} to fetch content...")
                
                # 如果是 base64 编码的 URL，先解码
                actual_url = base64.b64decode(url).decode() if '==' in url else url
                if actual_url.startswith(('clan://', 'file://', 'proxy://')):
                    actual_url = base_url

                response = session.get(
                    actual_url,
                    headers=headers,
                    timeout=30,
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
                
                print("No valid M3U content found, trying next format...")
                time.sleep(retry_delay)

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                continue

    print("All URL formats failed")
    raise Exception("Failed to fetch M3U content")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    process_m3u() 