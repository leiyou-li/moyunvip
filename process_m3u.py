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

    # 设置完整的请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache'
    }

    # 获取原始 M3U 内容
    url = "https://tv.iill.top/m3u/Gather"
    max_retries = 3
    retry_delay = 5  # 秒

    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            content = response.text

            # 检查是否获取到了正确的 M3U 内容
            if not content.startswith('#EXTM3U'):
                raise ValueError("Invalid M3U content received")

            # 处理内容，保留原有分类和频道信息
            lines = content.split('\n')
            processed_lines = []
            
            # 添加 EPG 源信息到文件开头
            processed_lines.append('#EXTM3U x-tvg-url="http://epg.51zmt.top:8000/e.xml"')
            for line in lines:
                if line.startswith('#EXTINF:'):
                    # 保留原有的分组信息
                    group_match = re.search(r'group-title="([^"]*)"', line)
                    group_title = group_match.group(1) if group_match else "IPTV"
                    
                    # 获取频道名称
                    channel_name = re.search(r',(.+)$', line)
                    if channel_name:
                        name = channel_name.group(1).strip()
                        # 保留原有属性，只添加缺少的 EPG 属性
                        if 'tvg-id="' not in line:
                            line = line.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-id="{name}"')
                        if 'tvg-name="' not in line:
                            line = line.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-name="{name}"')
                    processed_lines.append(line)
                elif line.strip() and not line.startswith('#EXTM3U'):
                    # 保留所有非空的URL行
                    processed_lines.append(line)
            
            # 保存处理后的内容
            with open('moyun.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(processed_lines))
            
            print("Successfully updated M3U content")
            break  # 成功获取数据，跳出重试循环

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Failed to fetch M3U content after all retries")
                raise

if __name__ == "__main__":
    process_m3u() 