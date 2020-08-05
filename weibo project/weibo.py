import requests
import urllib
import base64
import time
import re
import json
import rsa
import binascii
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from requests.packages.urllib3.connectionpool import InsecureRequestWarning

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://weibo.com/?sudaref=www.baidu.com&display=0&retcode=6102',
    'Connection': 'keep-alive'
}
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Login():
    def __init__(self):
        self.get_pre_login_save=self.get_pre_login()
    session = requests.session()
    user_name = "18516260359"
    pass_word = "zhuyilong"


    def get_username(self):
        return base64.b64encode(urllib.parse.quote(self.user_name).encode("utf-8")).decode("utf-8")

    def get_pre_login(self):
        # 取servertime, nonce,pubkey
        # int(time.time() * 1000)
        params = {
            "entry": "weibo",
            "callback": "sinaSSOController.preloginCallBack",
            "su": self.get_username(),
            "rsakt": "mod",
            "checkpin": "1",
            "client": "ssologin.js(v1.4.19)",
            "_": int(time.time() * 1000)
        }
        try:
            response = self.session.post("https://login.sina.com.cn/sso/prelogin.php", params=params, headers=header,
                                         verify=False)
            #print(json.loads(re.search(r"\((?P<data>.*)\)", response.text).group("data")))
            return json.loads(re.search(r"\((?P<data>.*)\)", response.text).group("data"))
        except:
            print("获取公钥失败")
            return 0

    def get_password(self):
        public_key = rsa.PublicKey(int(self.get_pre_login_save["pubkey"], 16), int("10001", 16))
        password_string = str(self.get_pre_login_save["servertime"]) + '\t' + str(self.get_pre_login_save["nonce"]) + '\n' + self.pass_word
        #password=binascii.b2a_hex(rsa.encrypt(password_string.encode("utf-8"), public_key)).decode("utf-8")
        #print(password)
        return binascii.b2a_hex(rsa.encrypt(password_string.encode("utf-8"), public_key)).decode("utf-8")

    def login(self):
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "qrcode_flag": "false",
            "useticket": "1",
            "vsnf": "1",
            "su": self.get_username(),
            "service": "miniblog",
            "servertime": self.get_pre_login_save["servertime"],
            "nonce": self.get_pre_login_save["nonce"],
            "pwencode": "rsa2",
            "rsakv": self.get_pre_login_save["rsakv"],
            "sp": self.get_password(),
            "sr": "1536*864",
            "encoding": "UTF-8",
            "prelt": "529",
            "url": "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "TEXT"
        }
        login_data = self.session.post("https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)",
                                       data=post_data, headers=header, verify=False)
        #print(login_data.json())
        params = {
            "ticket": login_data.json()['ticket'],
            "ssosavestate": int(time.time()),
            "callback": "sinaSSOController.doCrossDomainCallBack",
            "scriptId": "ssoscript0",
            "client": "ssologin.js(v1.4.19)",
            "_": int(time.time() * 1000)
        }
        self.session.post("https://passport.weibo.com/wbsso/login", params=params, verify=False, headers=header)
        return self.session


login = Login()
session=login.login()
'''
#login 测试代码
#response=session.post("http://weibo.com",verify=False,headers=header)
#soup=BeautifulSoup(response.text,"html.parser")
#print(soup.find('title'))
'''



def get_page_session(date):
    time.sleep(2)
    return session.post("https://s.weibo.com/weibo/%25E6%259D%258E%25E6%2596%25BD%25E5%25BE%25B7%25E6%259E%2597?topnav=1&wvr=6&b=1",verify=False,headers=header)

def get_data_session(date,page):
    time.sleep(2)
    return session.post(
        "https://s.weibo.com/weibo/%25E6%259D%258E%25E6%2596%25BD%25E5%25BE%25B7%25E6%259E%2597?topnav=1&wvr=6&b=1&page={c}".format(c=page),
        verify=False, headers=header)

def get_page_res(date):
    try:
        return get_page_session(date)
    except:
        try:
            return get_page_session(date)
        except:
            print("获取页码信息失败",date)
            return 0

def get_data_res(date,page):
    try:
        return get_data_session(date,page)
    except:
        try:
            return get_data_session(date,page)
        except:
            print("获取数据信息失败",date,page)
            return 0


def get_page(date):
    response =get_page_res(date)
    if response:
        soup=BeautifulSoup(response.text,"html.parser")
        try:
            pages=soup.find("ul","s-scroll").find_all("li")
            return len(pages)
        except:
            print("获取页码失败",date)
            return 0

def get_data(data,page):
    response=get_data_res(data,page)
    cri_data=[]
    if response:
        try:
            soup=BeautifulSoup(response.text,"html.parser")
            infos=soup.find_all('div',"content")        #微博内容
            records=soup.find_all("div","card-act")     #微博内容的评论
            for info,record in zip(infos[0:],records[0:]):
                #分别为作者，内容和时间
                try:
                    zyz1=info.find("a", "name").text
                except:
                    zyz1=''
                zyz2=info.find("p", "txt").text.strip()
                try:
                    zyz3=info.find("p", "from").text.split()[0]
                except:
                    zyz3=''
                try:
                    recs = record.find_all('li')
                    zyz4=re.findall(r'转发 (.+?)', recs[1].text, re.S)
                    zyz5=re.findall(r'评论 (.+?)', recs[2].text, re.S)
                except:
                    zyz4=''
                    zyz5=''
                temp=[zyz1,zyz2,zyz3,zyz4,zyz5]
                cri_data.append(temp)

            #print(cri_data[0])
            #print(type(cri_data[0]))
            #返回值为列表组成的列表，列表中的每一个元素都是[作者，内容，时间]
        except:pass
    return cri_data

df = pd.DataFrame(columns=['name', 'content','time','forward','comments'])

currpage=get_page(2019)
for i in range(currpage):
    cri_data=get_data(2019,i+1)
    for each in cri_data:
        df = df.append({'name': each[0], 'content': each[1], 'time': each[2],'forward':each[3],'comments':each[4]}, ignore_index=True)


df.to_csv(r'C:\Users\chrise\Desktop\temp1.csv')








