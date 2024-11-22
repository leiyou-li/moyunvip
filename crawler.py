import requests
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup
import logging
import socket
import concurrent.futures
from urllib.parse import urlparse
import subprocess
import time

class IPTVCrawler:
    def __init__(self):
        self.categories = {
            "央视": r"CCTV|央视",
            "卫视": r"卫视",
            "港澳台": r"凤凰|TVB|香港|澳门|台湾",
            "国际": r"CNN|BBC|NHK",
            "北京": r"北京\w*台|BTV|首都台",
            "上海": r"上海\w*台|东方台|STV",
            "天津": r"天津\w*台|TJTV",
            "重庆": r"重庆\w*台|CQTV",
            "黑龙江": r"黑龙江\w*台|哈尔滨",
            "吉林": r"吉林\w*台|长春",
            "辽宁": r"辽宁\w*台|沈阳|大连",
            "内蒙古": r"内蒙古\w*台|呼和浩特",
            "河北": r"河北\w*台|石家庄",
            "新疆": r"新疆\w*台|乌鲁木齐",
            "甘肃": r"甘肃\w*台|兰州",
            "青海": r"青海\w*台|西宁",
            "陕西": r"陕西\w*台|西安",
            "宁夏": r"宁夏\w*台|银川",
            "河南": r"河南\w*台|郑州",
            "山东": r"山东\w*台|济南|青岛",
            "山西": r"山西\w*台|太原",
            "安徽": r"安徽\w*台|合肥",
            "湖北": r"湖北\w*台|武汉",
            "湖南": r"湖南\w*台|长沙",
            "江苏": r"江苏\w*台|南京|苏州",
            "浙江": r"浙江\w*台|杭州|宁波",
            "江西": r"江西\w*台|南昌",
            "福建": r"福建\w*台|福州|厦门",
            "广东": r"广东\w*台|深圳|广州",
            "广西": r"广西\w*台|南宁",
            "云南": r"云南\w*台|昆明",
            "贵州": r"贵州\w*台|贵阳",
            "四川": r"四川\w*台|成都",
            "西藏": r"西藏\w*台|拉萨",
            "海南": r"海南\w*台|海口|三亚",
            "其他": r".*"
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 添加FFmpeg检测配置
        self.ffmpeg_timeout = 15  # 检测超时时间（秒）
        self.max_check_workers = 10  # 并发检测数量
        self.quality_cache = {}  # 缓存质量检测结果

    def _check_ip_version(self, url):
        """检查URL的IP版本"""
        try:
            hostname = urlparse(url).hostname
            if not hostname:
                return "unknown"
            
            # 获取所有IP地址（IPv4和IPv6）
            addresses = socket.getaddrinfo(hostname, None)
            
            has_ipv4 = any(addr[0] == socket.AF_INET for addr in addresses)
            has_ipv6 = any(addr[0] == socket.AF_INET6 for addr in addresses)
            
            if has_ipv4 and has_ipv6:
                return "both"
            elif has_ipv4:
                return "ipv4"
            elif has_ipv6:
                return "ipv6"
            else:
                return "unknown"
        except:
            return "unknown"

    def search_iptv_sources(self):
        """搜索网络上的IPTV直播源"""
        sources = []
        
        # 搜索GitHub上的IPTV资源
        github_urls = self._search_github_sources()
        sources.extend(github_urls)
        
        # 搜索其他网站的IPTV资源
        other_urls = self._search_other_sources()
        sources.extend(other_urls)
        
        # 搜索IPTV提供商的公开资源
        provider_urls = self._search_provider_sources()
        sources.extend(provider_urls)
        
        return list(set(sources))  # 去重

    def _search_github_sources(self):
        """搜索GitHub上的IPTV资源"""
        urls = []
        try:
            # 扩展搜索关键词
            search_queries = [
                "extension:m3u+iptv+china",
                "extension:m3u8+iptv+china",
                "filename:playlist.m3u",
                "filename:tv.m3u",
                "filename:china.m3u"
            ]
            
            for query in search_queries:
                search_url = f"https://api.github.com/search/code?q={query}"
                response = requests.get(search_url, headers=self.headers)
                if response.status_code == 200:
                    results = response.json().get('items', [])
                    for item in results:
                        raw_url = item['html_url'].replace('github.com', 'raw.githubusercontent.com')
                        raw_url = raw_url.replace('/blob', '')
                        urls.append(raw_url)
                        
        except Exception as e:
            self.logger.error(f"GitHub搜索错误: {str(e)}")
        return urls

    def _search_other_sources(self):
        """搜索其他网站的IPTV资源"""
        urls = []
        try:
            # 搜索常见的IPTV资源分享网站
            iptv_sites = [
                "https://iptv-org.github.io/iptv/countries/cn.m3u",
                "https://iptv-org.github.io/iptv/categories/news.m3u",
                "https://iptv-org.github.io/iptv/categories/entertainment.m3u"
            ]
            
            for site in iptv_sites:
                response = requests.get(site, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    urls.append(site)
                    
        except Exception as e:
            self.logger.error(f"其他源搜索错误: {str(e)}")
        return urls

    def _search_provider_sources(self):
        """搜索IPTV提供商的公开资源"""
        urls = []
        try:
            # 这里可以添加已知的IPTV提供商直播源
            provider_urls = [
                # 添加可靠的IPTV提供商URL
            ]
            urls.extend(provider_urls)
        except Exception as e:
            self.logger.error(f"提供商源搜索错误: {str(e)}")
        return urls

    def _check_stream_availability(self, url):
        """检测直播源是否可用"""
        try:
            # FFmpeg命令：尝试读取流的前几帧
            command = [
                'ffmpeg',
                '-timeout', str(self.ffmpeg_timeout * 1000000),  # 微秒
                '-i', url,
                '-t', '3',  # 只读取3秒
                '-f', 'null',
                '-'
            ]
            
            # 执行FFmpeg命令
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            try:
                # 等待进程完成，设置超时时间
                process.wait(timeout=self.ffmpeg_timeout)
                
                # 检查返回码
                if process.returncode == 0:
                    return True
                else:
                    stderr = process.stderr.read().decode('utf-8', errors='ignore')
                    self.logger.debug(f"Stream check failed for {url}: {stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                # 超时时终止进程
                process.kill()
                self.logger.debug(f"Stream check timeout for {url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking stream {url}: {str(e)}")
            return False

    def _check_stream_quality(self, url):
        """检测直播源质量"""
        try:
            if url in self.quality_cache:
                return self.quality_cache[url]
                
            start_time = time.time()
            
            # FFmpeg命令：检测流的质量
            command = [
                'ffmpeg',
                '-timeout', str(self.ffmpeg_timeout * 1000000),
                '-i', url,
                '-t', '3',  # 读取3秒
                '-f', 'null',
                '-'
            ]
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            try:
                # 等待进程完成
                process.wait(timeout=self.ffmpeg_timeout)
                
                if process.returncode == 0:
                    # 计算响应时间
                    response_time = time.time() - start_time
                    
                    # 分析FFmpeg输出以获取更多质量指标
                    stderr = process.stderr.read().decode('utf-8', errors='ignore')
                    
                    # 计算质量分数 (0-100)
                    quality_score = self._calculate_quality_score(response_time, stderr)
                    
                    self.quality_cache[url] = quality_score
                    return quality_score
                    
                return 0
                
            except subprocess.TimeoutExpired:
                process.kill()
                return 0
                
        except Exception as e:
            self.logger.error(f"质量检测错误 {url}: {str(e)}")
            return 0
            
    def _calculate_quality_score(self, response_time, ffmpeg_output):
        """计算质量分数"""
        score = 100
        
        # 根据响应时间扣分（响应时间越短越好）
        if response_time > 5:
            score -= 40
        elif response_time > 3:
            score -= 20
        elif response_time > 1:
            score -= 10
            
        # 分析FFmpeg输出
        if 'speed=' in ffmpeg_output:
            # 提取处理速度
            speed_match = re.search(r'speed=\s*([\d.]+)x', ffmpeg_output)
            if speed_match:
                speed = float(speed_match.group(1))
                if speed < 1:
                    score -= 20
                elif speed < 2:
                    score -= 10
                    
        # 检查是否有错误或警告
        if 'error' in ffmpeg_output.lower():
            score -= 30
        if 'warning' in ffmpeg_output.lower():
            score -= 10
            
        return max(0, score)  # 确保分数不小于0

    def verify_channels(self, channels):
        """验证所有频道的可用性并评估质量"""
        verified_channels = []
        total_channels = len(channels)
        
        self.logger.info(f"开始验证和评估 {total_channels} 个频道...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_check_workers) as executor:
            future_to_channel = {
                executor.submit(self._verify_and_check_quality, channel): channel 
                for channel in channels
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_channel):
                channel = future_to_channel[future]
                completed += 1
                
                try:
                    result = future.result()
                    if result:
                        verified_channels.append(result)
                        self.logger.info(f"进度: {completed}/{total_channels} - 验证成功: {channel['name']} (质量分数: {result['quality_score']})")
                    else:
                        self.logger.info(f"进度: {completed}/{total_channels} - 验证失败: {channel['name']}")
                except Exception as e:
                    self.logger.error(f"验证出错 {channel['name']}: {str(e)}")
        
        # 按质量分数排序
        verified_channels.sort(key=lambda x: x['quality_score'], reverse=True)
        
        end_time = time.time()
        duration = end_time - start_time
        success_rate = (len(verified_channels) / total_channels) * 100
        
        self.logger.info(f"验证完成: 总共 {total_channels} 个频道")
        self.logger.info(f"有效频道: {len(verified_channels)} 个 ({success_rate:.1f}%)")
        self.logger.info(f"耗时: {duration:.1f} 秒")
        
        return verified_channels

    def _verify_and_check_quality(self, channel):
        """验证单个频道并检测质量"""
        if self._check_stream_availability(channel['url']):
            quality_score = self._check_stream_quality(channel['url'])
            channel['quality_score'] = quality_score
            return channel
        return None

    def fetch_sources(self):
        """获取所有直播源"""
        all_channels = []
        sources = self.search_iptv_sources()
        self.logger.info(f"找到 {len(sources)} 个直播源")
        
        # 使用线程池加速获取过程
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(self._fetch_single_source, source): source 
                for source in sources
            }
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    channels = future.result()
                    if channels:
                        all_channels.extend(channels)
                        self.logger.info(f"从 {url} 成功获取 {len(channels)} 个频道")
                except Exception as e:
                    self.logger.error(f"获取直播源失败 {url}: {str(e)}")
        
        # 验证频道可用性
        self.logger.info("开始验证频道可用性...")
        verified_channels = self.verify_channels(all_channels)
        
        return verified_channels

    def _fetch_single_source(self, source):
        """获取单个源的频道列表"""
        try:
            response = requests.get(source, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return self._parse_m3u(response.text)
        except Exception as e:
            self.logger.error(f"获取源失败 {source}: {str(e)}")
        return []

    def _parse_m3u(self, content):
        """解析M3U文件内容"""
        channels = []
        lines = content.split('\n')
        current_channel = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#EXTINF:'):
                # 尝试不同的匹配模式
                channel_name = None
                name_patterns = [
                    r'tvg-name="(.*?)"',
                    r',(.*?)$',
                    r'group-title="(.*?)"'
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, line)
                    if match:
                        channel_name = match.group(1)
                        break
                
                if channel_name:
                    current_channel = {'name': channel_name}
                    
            elif line.startswith('http'):
                if current_channel:
                    current_channel['url'] = line
                    # 添加IP版本信息
                    current_channel['ip_version'] = self._check_ip_version(line)
                    channels.append(current_channel)
                    current_channel = None
        
        return channels

    def save_to_file(self, categorized_channels):
        """保存到文件，包含IP版本信息"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        # 保存 M3U 格式
        self._save_m3u_format(categorized_channels, timestamp)
        
        # 保存 TXT 格式
        self._save_txt_format(categorized_channels, timestamp)

    def _save_m3u_format(self, categorized_channels, timestamp):
        """保存M3U格式文件"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        output = f"#EXTM3U\n# 山海观雾提供 (更新时间：{timestamp})\n\n"
        
        # 优先输出主要分类
        main_categories = ["央视", "卫视", "港澳台", "国际"]
        for category in main_categories:
            if category in categorized_channels and categorized_channels[category]:
                output += f"# {category}\n"
                for channel in categorized_channels[category]:
                    ip_version = channel.get('ip_version', 'unknown')
                    output += f'#EXTINF:-1 tvg-name="{channel["name"]}" ip-version="{ip_version}",{channel["name"]}\n'
                    output += f'{channel["url"]}\n'
                output += "\n"
        
        # 然后输出各省地方台
        for category, channels in categorized_channels.items():
            if category not in main_categories and category != "其他" and channels:
                output += f"# {category}\n"
                for channel in channels:
                    ip_version = channel.get('ip_version', 'unknown')
                    output += f'#EXTINF:-1 tvg-name="{channel["name"]}" ip-version="{ip_version}",{channel["name"]}\n'
                    output += f'{channel["url"]}\n'
                output += "\n"
        
        # 最后输出其他类别
        if "其他" in categorized_channels and categorized_channels["其他"]:
            output += f"# 其他\n"
            for channel in categorized_channels["其他"]:
                ip_version = channel.get('ip_version', 'unknown')
                output += f'#EXTINF:-1 tvg-name="{channel["name"]}" ip-version="{ip_version}",{channel["name"]}\n'
                output += f'{channel["url"]}\n'
            output += "\n"
        
        with open('iptv.m3u', 'w', encoding='utf-8') as f:
            f.write(output)

    def _save_txt_format(self, categorized_channels, timestamp):
        """保存TXT格式文件，包含质量信息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        with open('iptv.txt', 'w', encoding='utf-8') as f:
            f.write(f"山海观雾提供 (更新时间：{timestamp})\n\n")
            
            # 优先输出主要分类
            main_categories = ["央视", "卫视", "港澳台", "国际"]
            for category in main_categories:
                if category in categorized_channels and categorized_channels[category]:
                    f.write(f"{category},#genre#\n")
                    for channel in categorized_channels[category]:
                        quality_info = f"[质量:{channel['quality_score']}]"
                        f.write(f"{channel['name']}{quality_info},{channel['url']}\n")
                    f.write("\n")
            
            # 然后输出各省地方台
            for category, channels in categorized_channels.items():
                if category not in main_categories and category != "其他" and channels:
                    f.write(f"{category},#genre#\n")
                    for channel in channels:
                        quality_info = f"[质量:{channel['quality_score']}]"
                        f.write(f"{channel['name']}{quality_info},{channel['url']}\n")
                    f.write("\n")
            
            # 最后输出其他类别
            if "其他" in categorized_channels and categorized_channels["其他"]:
                f.write(f"其他,#genre#\n")
                for channel in categorized_channels["其他"]:
                    quality_info = f"[质量:{channel['quality_score']}]"
                    f.write(f"{channel['name']}{quality_info},{channel['url']}\n")
                f.write("\n")

    def categorize_channels(self, channels):
        """对频道进行分类，并在每个分类中按质量排序"""
        categorized = {cat: [] for cat in self.categories.keys()}
        
        for channel in channels:
            categorized_flag = False
            for category, pattern in self.categories.items():
                if re.search(pattern, channel['name'], re.IGNORECASE):
                    categorized[category].append(channel)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                categorized['其他'].append(channel)
        
        # 对每个分类中的频道按质量排序
        for category in categorized:
            categorized[category].sort(key=lambda x: x['quality_score'], reverse=True)
        
        return categorized

if __name__ == "__main__":
    crawler = IPTVCrawler()
    channels = crawler.fetch_sources()
    categorized = crawler.categorize_channels(channels)
    crawler.save_to_file(categorized) 