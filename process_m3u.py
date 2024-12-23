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

def get_channel_category(name, original_category):
    # 特定分类的关键词映射
    category_keywords = {
        'CCTV': '央视频道',
        'CETV': '央视频道',
        '卫视': '卫视频道',
        'NewTV': 'NewTV频道',
        'iHOT': 'iHOT频道',
        'SiTV': '数字频道',
        '求索': '数字频道',
        '咪咕': '咪咕频道',
        'NBA': '咪咕「NBA」',
        '足球': '咪咕「足球」',
        '体育': '咪咕「体育」',
        'TV': '咪咕「TV」',
        'AKTV': '國際「AKTV�����',
        '香港': '港澳「限制」',
        '澳门': '港澳「限制」',
        '台湾': '台湾「限制」',
        '广东': '广东「特产」',
        '游戏': '游戏「赛事」',
        '轮播': '影视「轮播」',
        '广播': '广播「壹」',
        'KBS': '韩国「KO」',
        'MBC': '韩国「KO」',
        'SBS': '韩国「KO」',
        'WOWOW': '日本「JP」',
        'NHK': '日本「JP」'
    }
    
    # 检查频道名称中是否包含特定关键词
    for keyword, category in category_keywords.items():
        if keyword in name:
            return f"{category},#genre#"
    
    # 根据原始分类进行特殊处理
    if original_category:
        if '国际' in original_category:
            return '國際「匯集」,#genre#'
        elif '特色' in original_category:
            return '特色「混搭」,#genre#'
        elif '埋堆' in original_category:
            return '埋堆「轮播」,#genre#'
        elif '广播' in original_category and '贰' in original_category:
            return '广播「贰」,#genre#'
    
    # 如果没有匹配到特定分类，返回"其他"分类
    return '其他频道,#genre#'

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
                    # 根据频道名称确定分类
                    category = get_channel_category(name, current_category)
                    current_channel = {'name': name, 'category': category}
        elif not line.startswith('#'):
            # This is a URL line
            if current_channel and not skip_category and line not in seen_urls:
                # 跳过特定的URL
                if 'epg.iill.top/v/' not in line:
                    current_channel['url'] = line
                    channels.append(current_channel)
                    seen_urls.add(line)
                current_channel = {}
    
    # 对道进行分类排序，使用自定义排序顺序
    category_order = [
        '央视频道', '卫视频道', 'NewTV频道', 'iHOT频道', '数字频道',
        '地区频道', '咪咕「NBA」', '咪咕「足球」', '咪咕「体育」',
        '咪咕「TV」', '國際「AKTV」', '國際「匯集」', '港澳「限制」',
        '台湾「限制」', '广东「特产」', '特色「混搭」', '游戏「赛事」',
        '埋堆「轮播」', '影视「轮播」', '广播「壹」', '广播「贰」',
        '韩国「KO」', '日本「JP」'
    ]
    
    def get_cctv_order(name):
        """获取央视频道的排序权重"""
        if 'CCTV' not in name:
            return 999  # 非央视频道返回较大的数字
        
        # 处理特殊情况
        if 'CCTV5+' in name:
            return 5.5
        
        try:
            # 提取CCTV后面的数字
            number = re.search(r'CCTV(\d+)', name)
            if number:
                return float(number.group(1))
        except:
            pass
        
        return 999
    
    def get_category_order(channel):
        category = channel.get('category', '')
        if category is None:
            category = ''
        else:
            category = category.replace(',#genre#', '')
        
        name = channel.get('name', '')
        
        try:
            category_index = category_order.index(category)
            # 对央视频道进行特殊排序
            if category == '央视频道':
                return (category_index, get_cctv_order(name), name)
            return (category_index, name)
        except ValueError:
            return (len(category_order), name)
    
    channels.sort(key=get_category_order)
    return channels

def save_to_file(channels):
    with open('moyun.txt', 'w', encoding='utf-8') as f:
        # 获取当前时间
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 定义公告内容
        announcements = [
            {
                "channel": "墨韵更新日期",
                "entries": [
                    {"name": update_time, "url": "https://gitlab.com/lr77/IPTV/-/raw/main/%E8%B5%B7%E9%A3%8E%E4%BA%86.mp4"}
                ]
            }
        ]
        
        # 写入公告信息
        for announcement in announcements:
            f.write(f"{announcement['channel']},#genre#\n")
            for entry in announcement['entries']:
                if entry['name']:
                    f.write(f"{entry['name']},{entry['url']}\n")
                else:
                    f.write(f"{entry['url']}\n")
        f.write("\n")
        
        current_category = None
        
        for channel in channels:
            # 如果遇到新的分类，添加分类标题
            if channel.get('category') and channel['category'] != current_category:
                current_category = channel['category']
                f.write(f"{current_category}\n")
            
            # 写入频道信息
            if 'name' in channel and 'url' in channel:
                f.write(f"{channel['name']},{channel['url']}\n")

def main():
    content = fetch_m3u_content()
    channels = process_m3u(content)
    save_to_file(channels)

if __name__ == "__main__":
    main() 