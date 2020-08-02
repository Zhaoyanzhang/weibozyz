import datetime
import time
import pandas as pd
import pickle
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
#两种解析方法
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq


browser = webdriver.Chrome()
browser.get("https://auction.jd.com/sifa_list.html?childrenCateId=12728")
wait = WebDriverWait(browser, 20)
# class 后面跟两个属性，则需要加两个点
province=wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR,'.auction-content.auction-content-v2 .province'))
                 )
province.click()
myprovince=wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR,'.auction-content.auction-content-v2 .province.area-dl-drop [data-id="2"]'))
                 )
myprovince.click()
mystreet=wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR,'.auction-content.auction-content-v2 .city.area-dl-drop em'))
                 )
mystreet.click()

def index_page(page):
    try:
        # 找到最下面的下一页按钮,目前该方法对于京东法拍无法使用，不知道原因
        '''
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.page-wrap .ui-pager-next'))
        )
        input.click()
        '''
        time.sleep(5)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.goods-list li'))
        )
        # 获取房源数据
        urllist=get_products()
        print('请在5秒钟内点击下一页,总第%d页'%(page+1))
        return urllist
    except TimeoutException:
        index_page(page)

def get_products():
    html = browser.page_source
    doc = pq(html)

    items = doc('.pm-item a').items()
    houseurl = []
    for item in items:
        houseurl.append(item.attr('href'))
    return houseurl
    #不推荐以下写法，原因：find方法失效https://blog.csdn.net/ljy1067313358/article/details/88650250
    '''
        items = doc('.good-list .pm-item').items()
        for item in items:
            print(item.find('a').attr('href'))
    '''



def main():
    '''
    遍历每一页
    '''
    houseurl = []
    for i in range(1, 26):
        temp=index_page(i)
        houseurl.extend(temp)
    browser.quit()
    print('爬取结束')
    print('共有%d个房源地址'%(len(houseurl)))
    with open(r'C:\Users\chrise\Desktop\url.pkl','wb') as f:
        pickle.dump(houseurl,f)
    print('url已保存')


if __name__ == '__main__':
    main()