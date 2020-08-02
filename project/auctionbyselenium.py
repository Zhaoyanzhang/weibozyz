import datetime
import pickle
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,ElementNotVisibleException
#对于正在预告中的房源，起拍价保存在True_starting_price字段中


def get_info(url):
    browser = webdriver.Chrome()
    browser.get(url)
    wait = WebDriverWait(browser, 10)
    # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "grid")))
    print('网页已经加载')
    #点击‘我知道了’
    try:
        notice = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.dialog-submit'))
        )
        print('发现提示')
        notice.click()
        print('已点击提示')
    except TimeoutException:
        print('无提示')
    except ElementNotVisibleException:
        print('重新加载')
        notice1 = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.dialog-submit'))
        )
        notice1.click()
    finally:
        soup = BeautifulSoup(browser.page_source, "lxml")
        print('已获取网页')
    #房屋标题及地段
    try:
        bt=soup.select(".pm-name")[0].text
    except IndexError:  # 若读不到此项，则抛出list index out of range 错误，属于IndexError
        bt=''
    #起拍价 评估价 保证金 '拍卖说明起拍价：￥5,440,000评估价：￥7,757,561.5加价幅度：￥1,000保证金：￥540,000延时周期：5分钟/次?
    try:
        qpj=soup.select(".pm-tips")[0].text
    except IndexError:
        qpj = ''
    #拍卖时间 报名人数 '结束时间：\n    2020年03月23日 10:00:00\u30001人报名\u30002790人围观\u30009人关注提醒'
    #对于未开始房源，读不到此项信息，需要更新代码
    try:
        jssj=soup.select(".endtime")[0].text
        # 成交价   BUG: 这里可能读到成交价或者未开始房源的起拍价
        trueqpj=''
        try:
            cjj = soup.select(".lrc-tooltip-item")[0].text
        except IndexError:
            cjj = ''
    except IndexError:
        jssj=soup.select(".times")[0].text
        cjj = ''
        # 读到的大红字原本是成交价   但是对于未开始房源，这里是起拍价
        try:
            trueqpj = soup.select(".lrc-tooltip-item")[0].text
        except IndexError:
            trueqpj = ''
    #加价次数    '竞买公告竞买须知标的物详情保证金须知出价记录(0)优先购买权人相关帮助'
    try:
        num = soup.select('.pm-content .nav-item')[4].text
    except IndexError:
        num=''


    print('info got')
    browser.quit()
    print('quit')
    infor = [bt, qpj, cjj, jssj, num,trueqpj]
    return infor


def main():
    df = pd.DataFrame(columns=['title', 'starting_price', 'price', 'infor','count','True_starting_price'])
    # houseurl=['https://paimai.jd.com/112280147',
    #           'https://paimai.jd.com/111315151',
    #           'https://paimai.jd.com/115008831',#正在进行
    #           'https://paimai.jd.com/114918145'#预告中
    #           ,'https://paimai.jd.com/107342589'] #流拍

    houseurl=[]
    temphouseurl=[]
    with open(r'C:\Users\chrise\Desktop\url.pkl', 'rb') as f:
        temphouseurl = pickle.load(f)
    for i in temphouseurl:    #增加HTTPS协议头
        houseurl.append('https:'+i)

    prog=0
    for each in houseurl:
        prog=prog+1
        print('读取第%d个数据'%prog)
        info=get_info(each)
        df = df.append({'title': info[0], 'starting_price': info[1], 'price': info[2], 'infor': info[3],'count':info[4],'True_starting_price':info[5]}, ignore_index=True)

    df.to_csv(r'C:\Users\chrise\Desktop\temp.csv')



if __name__ == '__main__':
    main()
