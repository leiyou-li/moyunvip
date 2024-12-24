import requests
import re

def process_m3u():
    # 获取原始 M3U 内容
    url = "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u"
    response = requests.get(url)
    content = response.text
    
    # 添加 EPG 信息
    epg_url = "http://epg.51zmt.top:8000/api/diyp/"
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        if line.startswith('#EXTINF:'):
            # 在频道信息中添加 EPG tvg-id
            channel_name = re.search(r',(.+)$', line)
            if channel_name:
                name = channel_name.group(1).strip()
                # 添加 EPG 相关属性
                epg_info = f'#EXTINF:-1 tvg-id="{name}" tvg-name="{name}" tvg-logo="" group-title="IPTV",'
                processed_lines.append(epg_info + name)
        else:
            processed_lines.append(line)
    
    # 在文件开头添加 EPG 源信息
    header = '#EXTM3U x-tvg-url="http://epg.51zmt.top:8000/e.xml"\n'
    content = header + '\n'.join(processed_lines)
    
    # 保存处理后的内容
    with open('moyun.txt', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    process_m3u() 