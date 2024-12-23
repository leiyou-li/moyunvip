import requests
import re
from datetime import datetime

def fetch_m3u_content():
    sources = [
        "https://raw.githubusercontent.com/YanG-1989/m3u/refs/heads/main/Gather.m3u",
        "https://tv.iill.top/m3u/Gather"
    ]
    
    all_content = []
    for url in sources:
        try:
            response = requests.get(url)
            response.raise_for_status()
            all_content.append(response.text)
        except Exception as e:
            print(f"Error fetching M3U content from {url}: {e}")
    
    return '\n'.join(all_content) if all_content else None

def process_m3u(content):
    if not content:
        return []
    
    # Split content into lines and filter out empty lines
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Process lines to extract channel information
    channels = []
    current_channel = {}
    seen_urls = set()  # 用于去重
    current_category = None
    skip_categories = {'温馨「提示」', 'myTV「请到GitHub获取」'}  # 需要跳过的分类
    skip_category = False
    
    for line in lines:
        if line.startswith('#EXTINF:'):
            # Extract channel name
            name_match = re.search(r',(.*?)$', line)
            if name_match:
                name = name_match.group(1).strip()
                if name.startswith('•'):
                    # 去掉 • 符号，直接使用分类名
                    current_category = name[1:].strip()
                    # 检查是否是需要跳过的分类
                    skip_category = (current_category in skip_categories)
                    continue
                if not skip_category:  # 只有在不跳过的分类中才添加频道
                    current_channel = {'name': name, 'category': current_category}
        elif not line.startswith('#'):
            # This is a URL line
            if current_channel and not skip_category and line not in seen_urls:
                # 跳过特定的URL
                if 'epg.iill.top/v/' not in line:
                    current_channel['url'] = line
                    channels.append(current_channel)
                    seen_urls.add(line)
                current_channel = {}
    
    return channels

def save_to_file(channels):
    with open('moyun.txt', 'w', encoding='utf-8') as f:
        # 获取当前时间
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 写入固定的第一个分类��称、更新时间和MV地址
        f.write("墨韵提供,#genre#\n")
        f.write(f"更新时间：{update_time}\n")
        f.write("起风了,https://gitlab.com/lr77/IPTV/-/raw/main/%E8%B5%B7%E9%A3%8E%E4%BA%86.mp4\n")
        
        current_category = None
        
        for channel in channels:
            # 如果遇到新的分类，添加分类标题
            if channel.get('category') and channel['category'] != current_category:
                current_category = channel['category']
                # 修改分类标题格式
                f.write(f"\n{current_category},#genre#\n")
            
            # 写入频道信息
            if 'name' in channel and 'url' in channel:
                f.write(f"{channel['name']},{channel['url']}\n")

def main():
    content = fetch_m3u_content()
    channels = process_m3u(content)
    save_to_file(channels)

if __name__ == "__main__":
    main() 