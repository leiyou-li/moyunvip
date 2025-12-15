# coding = utf-8
# !/usr/bin/python
# 本资源来源于互联网公开渠道，仅可用于个人学习爬虫技术。
# 严禁将其用于任何商业用途，下载后请于 24 小时内删除，搜索结果均来自源站，本人不承担任何责任。
#by多弗朗明哥，可py内部填写,也可以和潇洒appget一样ext下面填写，外部填写会覆盖py内部填写
import re,sys,uuid,json,base64,urllib3,hashlib,time
from Crypto.Cipher import AES
from base.spider import Spider
from Crypto.Util.Padding import pad,unpad
sys.path.append('..')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Spider(Spider):
    def getName(self):
        return "潇洒版APPget"
        
    def init(self, extend=''):
        self.site_url = ""
        self.dataKey = ""
        self.dataIv = ""
        self.token = ""
        self.device_id = "1234567890ABCDEF"
        self.version = "1.0.0"
        self.ua = "okhttp/3.14.9"
        self.api_type = "getappapi"  
        
        if extend and extend.strip():
            try:
                ext = json.loads(extend.strip())
                
                site_url = ext.get('site', '')
                if site_url:
                    try:
                        response = self.fetch(site_url, headers={'User-Agent': self.ua}, timeout=10, verify=False)
                        if response.status_code == 200:
                            lines = response.text.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and (line.startswith('http://') or line.startswith('https://')):
                                    self.site_url = line.rstrip('/')
                                    break
                    except:
                        pass
                
                if not self.site_url:
                    self.site_url = ext.get('url', '')
                
                self.dataKey = ext.get('dataKey', '')
                self.dataIv = ext.get('dataIv', self.dataKey)
                self.token = ext.get('token', '')
                self.device_id = ext.get('deviceId', self.device_id)
                self.version = ext.get('version', self.version)
                self.ua = ext.get('ua', self.ua)
                self.api_type = ext.get('api', 'getappapi') 
                
            except Exception as e:
                print(f"配置解析错误: {e}")
        
        self.xurl = f"{self.site_url}/api.php/{self.api_type}"
        
        self.header = {
            'User-Agent': self.ua,
            'app-user-device-id': self.device_id,
            'app-version-code': self.version,
            'app-ui-mode': 'light',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        if self.token:
            self.header['app-user-token'] = self.token
        
        self.init_data = {}
        self.search_verify = False
        
        try:
            init_url = f"{self.xurl}.index/initV119"
            response = self.fetch(init_url, headers=self.header, verify=False)
            if response.status_code == 200:
                res_data = response.json()
                if 'data' in res_data:
                    encrypted_data = res_data['data']
                    decrypted_response = self.decrypt(encrypted_data)
                    self.init_data = json.loads(decrypted_response)
                    self.search_verify = self.init_data['config'].get('system_search_verify_status', False)
                    print("初始化成功")
                else:
                    print("初始化响应格式错误")
            else:
                print(f"初始化请求失败: {response.status_code}")
        except Exception as e:
            print(f"初始化异常: {e}")

    def homeContent(self, filter):
        if not self.init_data:
            return {
                "class": [
                    {"type_id": "1", "type_name": "电影"},
                    {"type_id": "2", "type_name": "电视剧"}, 
                    {"type_id": "3", "type_name": "动漫"},
                    {"type_id": "4", "type_name": "综艺"}
                ],
                "filters": {}
            }
            
        kjson = self.init_data
        result = {"class": [], "filters": {}}
        
        for i in kjson.get('type_list', []):
            type_name = i.get('type_name', '')
            if type_name in {'全部', 'QQ', 'juo.one'} or '企鹅群' in type_name:
                continue
                
            result['class'].append({
                "type_id": i.get('type_id', ''),
                "type_name": type_name
            })
            
            name_mapping = {'class': '类型', 'area': '地区', 'lang': '语言', 'year': '年份', 'sort': '排序'}
            filter_items = []
            
            for filter_type in i.get('filter_type_list', []):
                filter_name = filter_type.get('name')
                values = filter_type.get('list', [])
                if not values:
                    continue
                    
                value_list = [{"n": value, "v": value} for value in values]
                display_name = name_mapping.get(filter_name, filter_name)
                key = 'by' if filter_name == 'sort' else filter_name
                
                filter_items.append({
                    "key": key,
                    "name": display_name,
                    "value": value_list
                })
                
            type_id = i.get('type_id')
            if filter_items:
                result["filters"][str(type_id)] = filter_items
                
        return result

    def homeVideoContent(self):
        if not self.init_data:
            return {'list': []}
            
        videos = []
        kjson = self.init_data
        
        for i in kjson.get('type_list', []):
            for item in i.get('recommend_list', []):
                videos.append({
                    "vod_id": item.get('vod_id', ''),
                    "vod_name": item.get('vod_name', ''),
                    "vod_pic": item.get('vod_pic', ''),
                    "vod_remarks": item.get('vod_remarks', '')
                })
                
        return {'list': videos}

    def categoryContent(self, cid, pg, filter, ext):
        videos = []
        payload = {
            'area': ext.get('area', '全部'),
            'year': ext.get('year', '全部'),
            'type_id': cid,
            'page': str(pg),
            'sort': ext.get('sort', '最新'),
            'lang': ext.get('lang', '全部'),
            'class': ext.get('class', '全部')
        }
        
        url = f'{self.xurl}.index/typeFilterVodList'
        
        try:
            response = self.post(url=url, headers=self.header, data=payload, verify=False)
            if response.status_code == 200:
                res_data = response.json()
                if 'data' in res_data:
                    encrypted_data = res_data['data']
                    decrypted_response = self.decrypt(encrypted_data)
                    kjson1 = json.loads(decrypted_response)
                    
                    for i in kjson1.get('recommend_list', []):
                        videos.append({
                            "vod_id": i.get('vod_id', ''),
                            "vod_name": i.get('vod_name', ''),
                            "vod_pic": i.get('vod_pic', ''),
                            "vod_remarks": i.get('vod_remarks', '')
                        })
        except Exception as e:
            print(f"分类内容获取异常: {e}")
            
        return {'list': videos, 'page': int(pg), 'pagecount': 9999, 'limit': 90, 'total': 999999}

    def detailContent(self, ids):
        if not ids:
            return {'list': []}
            
        did = ids[0]
        videos = []
        
        api_endpoints = ['vodDetail', 'vodDetail2']
        
        for endpoint in api_endpoints:
            try:
                url = f'{self.xurl}.index/{endpoint}'
                payload = {'vod_id': did}
                
                response = self.post(url=url, headers=self.header, data=payload, verify=False)
                if response.status_code == 200:
                    response_data = response.json()
                    if 'data' in response_data:
                        encrypted_data = response_data['data']
                        kjson1 = self.decrypt(encrypted_data)
                        kjson = json.loads(kjson1)
                        break
            except:
                continue
        else:
            return {'list': []}
        
        play_form = ''
        play_url = ''
        lineid = 1
        name_count = {}
        
        for line in kjson.get('vod_play_list', []):
            player_info = line.get('player_info', {})
            player_show = player_info.get('show', '')
            
            keywords = {'防走丢', '群', '防失群', '官网'}
            if any(keyword in player_show for keyword in keywords):
                player_show = f'{lineid}线'
                
            count = name_count.get(player_show, 0) + 1
            name_count[player_show] = count
            if count > 1:
                player_show = f"{player_show}{count}"
                
            play_form += player_show + '$$$'
            
            parse = player_info.get('parse', '')
            parse_type = player_info.get('parse_type', '')
            player_parse_type = player_info.get('player_parse_type', '')
            
            kurls = ""
            for vod in line.get('urls', []):
                token = 'token+' + vod.get('token', '')
                kurls += f"{vod.get('name', '')}${parse},{vod.get('url', '')},{token},{player_parse_type},{parse_type}#"
            
            kurls = kurls.rstrip('#')
            play_url += kurls + '$$$'
            lineid += 1
        
        play_form = play_form.rstrip('$$$')
        play_url = play_url.rstrip('$$$')
        
        vod_info = kjson.get('vod', {})
        videos.append({
            "vod_id": did,
            "vod_name": vod_info.get('vod_name', ''),
            "vod_actor": vod_info.get('vod_actor', '').replace('演员', ''),
            "vod_director": vod_info.get('vod_director', '').replace('导演', ''),
            "vod_content": vod_info.get('vod_content', ''),
            "vod_remarks": vod_info.get('vod_remarks', ''),
            "vod_year": str(vod_info.get('vod_year', '')) + '年',
            "vod_area": vod_info.get('vod_area', ''),
            "vod_play_from": play_form,
            "vod_play_url": play_url
        })
        
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        try:
            aid = id.split(',')
            if len(aid) < 5:
                return {"parse": 0, "url": id, "header": self.header}
                
            uid = aid[0]
            kurl = aid[1]
            token = aid[2].replace('token+', '')
            player_parse_type = aid[3]
            parse_type = aid[4]
            
            if parse_type == '0':
                return {"parse": 0, "url": kurl, "header": self.header}
            elif parse_type == '2':
                return {"parse": 1, "url": uid + kurl, "header": self.header}
            elif player_parse_type == '2':
                response = self.fetch(url=f'{uid}{kurl}', headers=self.header, verify=False)
                if response.status_code == 200:
                    kjson1 = response.json()
                    return {"parse": 0, "url": kjson1.get('url', ''), "header": self.header}
            else:
                encrypted_url = self.encrypt(kurl)
                payload = {
                    'parse_api': uid,
                    'url': encrypted_url,
                    'player_parse_type': player_parse_type,
                    'token': token
                }
                url1 = f"{self.xurl}.index/vodParse"
                response = self.post(url=url1, headers=self.header, data=payload, verify=False)
                if response.status_code == 200:
                    response_data = response.json()
                    if 'data' in response_data:
                        encrypted_data = response_data['data']
                        kjson = self.decrypt(encrypted_data)
                        kjson1 = json.loads(kjson)
                        kjson2 = kjson1.get('json', '{}')
                        kjson3 = json.loads(kjson2)
                        url = kjson3.get('url', '')
                        return {"parse": 0, "playUrl": '', "url": url, "header": self.header}
        except Exception as e:
            print(f"播放内容处理异常: {e}")
            
        return {"parse": 0, "url": id, "header": self.header}

    def searchContent(self, key, quick, pg="1"):
        videos = []
        
        if 'xiaohys.com' in self.site_url:
            try:
                host = self.site_url.split('api.php')[0]
                data = self.fetch(f'{host}index.php/ajax/suggest?mid=1&wd={key}').json()
                for i in data.get('list', []):
                    videos.append({
                        "vod_id": i.get('id', ''),
                        "vod_name": i.get('name', ''),
                        "vod_pic": i.get('pic', '')
                    })
            except:
                pass
        else:
            payload = {
                'keywords': key,
                'type_id': "0",
                'page': str(pg)
            }
            
            if self.search_verify:
                verifi = self.verification()
                if verifi is not None:
                    payload['code'] = verifi['code']
                    payload['key'] = verifi['uuid']
            
            url = f'{self.xurl}.index/searchList'
            
            try:
                response = self.post(url=url, data=payload, headers=self.header, verify=False)
                if response.status_code == 200:
                    res_data = response.json()
                    if res_data.get('data'):
                        encrypted_data = res_data['data']
                        kjson = self.decrypt(encrypted_data)
                        kjson1 = json.loads(kjson)
                        
                        for i in kjson1.get('search_list', []):
                            videos.append({
                                "vod_id": i.get('vod_id', ''),
                                "vod_name": i.get('vod_name', ''),
                                "vod_pic": i.get('vod_pic', ''),
                                "vod_remarks": f"{i.get('vod_year', '')} {i.get('vod_class', '')}"
                            })
                    else:
                        return {'list': [], 'msg': res_data.get('msg', '')}
            except Exception as e:
                print(f"搜索异常: {e}")
                
        return {'list': videos, 'page': int(pg), 'pagecount': 9999, 'limit': 90, 'total': 999999}

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def decrypt(self, encrypted_data_b64):
        try:
            key_bytes = self.dataKey.encode('utf-8')
            iv_bytes = self.dataIv.encode('utf-8')
            encrypted_data = base64.b64decode(encrypted_data_b64)
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
            decrypted_padded = cipher.decrypt(encrypted_data)
            decrypted = unpad(decrypted_padded, AES.block_size)
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"解密异常: {e}")
            return "{}"

    def encrypt(self, data):
        try:
            key_bytes = self.dataKey.encode('utf-8')
            iv_bytes = self.dataIv.encode('utf-8')
            data_bytes = data.encode('utf-8')
            padded_data = pad(data_bytes, AES.block_size)
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
            encrypted_bytes = cipher.encrypt(padded_data)
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            print(f"加密异常: {e}")
            return ""

    def verification(self):
        try:
            random_uuid = str(uuid.uuid4())
            dat = self.fetch(f'{self.xurl}.verify/create?key={random_uuid}', headers=self.header, verify=False).content
            base64_img = base64.b64encode(dat).decode('utf-8')
            if not dat:
                return None
            code = self.ocr(base64_img)
            if not code:
                return None
            code = self.replace_code(code)
            if not (len(code) == 4 and code.isdigit()):
                return None
            return {'uuid': random_uuid, 'code': code}
        except:
            return None

    def ocr(self, base64img):
        try:
            dat2 = self.post("https://api.nn.ci/ocr/b64/text", data=base64img, headers=self.header, verify=False).text
            return dat2
        except:
            return None

    def replace_code(self, text):
        replacements = {'y': '9', '口': '0', 'q': '0', 'u': '0', 'o': '0', '>': '1', 'd': '0', 'b': '8', '已': '2','D': '0', '五': '5'}
        if len(text) == 3:
            text = text.replace('566', '5066')
            text = text.replace('066', '1666')
        return ''.join(replacements.get(c, c) for c in text)