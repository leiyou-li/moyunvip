import requests
import re
import time
import asyncio
from playwright.async_api import async_playwright

async def process_m3u():
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("Accessing URL...")
            await page.goto("https://tv.iill.top/m3u/Gather")
            
            # 等待页面加载
            await page.wait_for_load_state('networkidle')
            content = await page.content()
            print("Content retrieved")
            
            # 检查是否获取到了正确的 M3U 内容
            if '#EXTM3U' in content:
                print("Found M3U content")
                # 提取实际的 M3U 内容
                content = content.split('#EXTM3U', 1)[1]
                content = '#EXTM3U' + content
                
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
                
            else:
                print("No valid M3U content found")
                print("Page content preview:", content[:500])
                raise ValueError("Invalid content received")
                
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            raise
            
        finally:
            await browser.close()
            print("Browser closed")

if __name__ == "__main__":
    asyncio.run(process_m3u()) 