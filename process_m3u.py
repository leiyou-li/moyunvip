import requests
import re

def process_m3u():
    # 获取原始 M3U 内容
    url = "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u"
    response = requests.get(url)
    content = response.text
    
    # 直接将内容写入文件，保持 M3U 格式
    with open('moyun.txt', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    process_m3u() 