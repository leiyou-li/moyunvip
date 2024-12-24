import cloudscraper
import re
import time

def process_m3u():
    # 创建一个 CloudScraper 实例
    scraper = cloudscraper.create_scraper()

    # 获取原始 M3U 内容，添加重试机制
    url = "https://tv.iill.top/m3u/Gather"
    max_retries = 3
    retry_delay = 5  # 秒

    for attempt in range(max_retries):
        try:
            response = scraper.get(url, timeout=30)
            response.raise_for_status()  # 检查响应状态
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