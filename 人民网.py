import requests  # 发起网络请求
from bs4 import BeautifulSoup  # 解析HTML文本
import pandas as pd  # 处理数据
import os
import time  # 处理时间戳
import json  # 用来解析json文本

"""
用于发起网络请求，获取目标页面的源码
:param url: 目标页面的url
:param kw: 检索的关键词
:param page: 页码
:return: html页面源码
"""
def fetchUrl(url, kw, page):
    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:106.0) Gecko/20100101 Firefox/106.0',
        "Content-Type": "application/json",
        'Cookie': '__jsluid_h=7b094980f877a51bcbe915df4880e317; sso_c=0',
        'Host': 'search.people.cn',
        'Origin': 'http://search.people.cn',
        'Referer': 'http://search.people.cn/s/?keyword=%E6%8A%A4%E5%A3%AB&st=0&_=1666959944682'
    }

    # 请求参数
    payloads = {
        "endTime": 0,
        "hasContent": True,
        "hasTitle": True,
        "isFuzzy": True,
        "key": kw,
        "limit": 10,
        "page": page,
        "sortType": 2,
        "startTime": 0,
        "type": 0,
    }

    # 发起 post 请求
    r = requests.post(url, headers=headers, data=json.dumps(payloads))
    return r.json()

"""
解析josn数据，并返回博文内容
:param jsonObj: 需要解析的json对象
:return: 返回博文内容
"""
def parseJson(jsonObj):
    # 解析数据
    records = jsonObj["data"]["records"];
    for item in records:
        # 这里示例解析了几条，其他数据项如末尾所示，有需要自行解析
        pid = item["id"]
        originalName = item["originalName"]
        belongsName = item["belongsName"]
        content = BeautifulSoup(item["content"], "html.parser").text
        displayTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["displayTime"] / 1000))
        subtitle = item["subtitle"]
        title = BeautifulSoup(item["title"], "html.parser").text
        url = item["url"]

        yield [[pid, title, subtitle, displayTime, originalName, belongsName, content, url]]


'''
用于将数据保存成 csv 格式的文件（以追加的模式）
path   : 保存的路径，若文件夹不存在，则自动创建
filename: 保存的文件名
data   : 保存的数据内容
'''
def saveFile(path, filename, data):
    # 如果路径不存在，就创建路径
    if not os.path.exists(path):
        os.makedirs(path)
    # 保存数据
    dataframe = pd.DataFrame(data=data)
    dataframe.to_csv(path + filename + ".csv", encoding='utf_8_sig', mode='a', index=False, sep=',', header=False)

"""
生成博文的csv文件
:param kw: 检索关键字
:param start_page: 开始页码
:param end_page: 结束页码
"""
def getcsv(kw, start_page, end_page):

    filename = '人民网_' + kw
    path = './data/' + filename + '.csv'
    if os.path.exists(path):
        os.remove(path)
    # 保存表头行
    headline = [["文章id", "标题", "副标题", "发表时间", "来源", "版面", "摘要", "链接"]]
    saveFile("./data/", filename, headline)
    # 爬取数据
    for page in range(int(start_page), int(end_page) + 1):
        # 人民网检索的接口api
        url = "http://search.people.cn/search-platform/front/search"
        html = fetchUrl(url, kw, page)
        for data in parseJson(html):
            saveFile("./data/", filename, data)
        print("第{}页爬取完成".format(page))

    # 爬虫完成提示信息
    print("爬虫执行完毕！数据已保存至以下路径中，请查看！")
    print(os.getcwd(), "/data")


if __name__ == "__main__":
    kw = input('请输入关键词：')
    start_page = input('请输入开始页码：')
    end_page = input('请输入结束页码：')

    getcsv(kw, start_page, end_page)
