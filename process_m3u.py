import requests
import re
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def process_m3u():
    # 创建 session 并设置重试策略
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # 尝试不同的 URL 格式和参数
    urls = [
        "https://tv.iill.top/m3u/Gather",
        "https://tv.iill.top/m3u/gather",  # 小写
        "https://tv.iill.top/m3u/gather.m3u",  # 添加扩展名
        "https://tv.iill.top/m3u/gather.m3u8",
        "https://tv.iill.top/m3u/gather.txt",
        "https://tv.iill.top/m3u/gather?type=txt",
        "https://tv.iill.top/m3u/gather?format=m3u",
        "https://tv.iill.top/m3u/gather?t=" + str(int(time.time()))  # 添加时间戳
    ]

    headers = {
        'User-Agent': 'okhttp/3.12.0',
        'Accept': '*/*',
        'Connection': 'keep-alive',
    }

    for url in urls:
        try:
            print(f"\nTrying URL: {url}")
            response = session.get(url, headers=headers, timeout=30)
            content = response.text
            print(f"Status code: {response.status_code}")
            print(f"Content preview: {content[:200]}")  # 打印内容预览

            if content.startswith('#EXTM3U'):
                print("Found valid M3U content!")
                
                # 处理内容
                lines = content.split('\n')
                processed_lines = []
                
                # 添加 EPG 源信息到文件开头
                processed_lines.append('#EXTM3U x-tvg-url="https://epg.iill.top/epg"')
                for line in lines:
                    if line.startswith('#EXTINF:'):
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
                    elif line.strip() and not line.startswith('#EXTM3U'):
                        processed_lines.append(line)
                
                # 保存处理后的内容
                with open('moyun.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(processed_lines))
                
                print("Successfully updated M3U content")
                return

        except Exception as e:
            print(f"Error with URL {url}: {str(e)}")
            continue

    raise Exception("All URL formats failed")

if __name__ == "__main__":
    process_m3u() 