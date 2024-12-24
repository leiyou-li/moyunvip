import requests
import re
import time
import json

def get_options_headers():
    """获取 OPTIONS 请求头"""
    return {
        'authority': 'api.lige.chat',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'access-control-request-headers': 'content-type',
        'access-control-request-method': 'POST',
        'origin': 'https://lige.chat',
        'referer': 'https://lige.chat/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    }

def get_post_headers():
    """获取 POST 请求头"""
    return {
        'authority': 'api.lige.chat',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'content-type': 'application/json',
        'origin': 'https://lige.chat',
        'referer': 'https://lige.chat/',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    }

def process_m3u():
    session = requests.Session()
    api_url = "https://api.lige.chat/ua"
    target_url = "https://tv.iill.top/m3u/Gather"
    
    try:
        print("Sending OPTIONS request...")
        # 发送 OPTIONS 请求
        options_response = session.options(
            api_url,
            headers=get_options_headers(),
            verify=True
        )
        print(f"OPTIONS response status: {options_response.status_code}")
        
        # 等待一小段时间模拟真实请求
        time.sleep(1)
        
        print("Sending POST request...")
        # 发送 POST 请求
        response = session.post(
            api_url,
            headers=get_post_headers(),
            json={'url': target_url},
            verify=True
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                content = response.json()
                if isinstance(content, dict) and 'data' in content:
                    m3u_content = content['data']
                else:
                    m3u_content = response.text
            except:
                m3u_content = response.text
            
            print(f"Content preview: {str(m3u_content)[:200]}")
            
            # 检查并处理 M3U 内容
            if '#EXTM3U' in str(m3u_content):
                print("Found M3U content")
                lines = str(m3u_content).split('\n')
                processed_lines = []
                
                # 添加 EPG 源信息到文件开头
                processed_lines.append('#EXTM3U x-tvg-url="https://epg.iill.top/epg"')
                
                current_group = None
                for line in lines:
                    line = line.strip()
                    if not line or line == '#EXTM3U':
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
                
                if len(processed_lines) > 1:
                    # 保存处理后的内容
                    with open('moyun.txt', 'w', encoding='utf-8') as f:
                        f.write('\n'.join(processed_lines))
                    
                    print("Successfully updated M3U content")
                    print(f"Processed {len(processed_lines)} lines")
                    return
                else:
                    print("No valid channel information found")
            else:
                print("No M3U content found in response")
                print("Full response:", m3u_content)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

    print("Failed to fetch content from API")
    raise Exception("Failed to fetch M3U content")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    process_m3u() 