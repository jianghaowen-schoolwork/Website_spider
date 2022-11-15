import time
import requests
from lxml import etree
from tool_weibo import Excel
import calendar


def get_per_url(str_time):
    """
    获取每一页的url
    :return:
    """
    for i in range(0, 24):
        start_time = str_time + '-' + addZero(i)
        end_time = str_time + '-' + addZero(i + 1)

        base_url = 'https://s.weibo.com/weibo?q=%E6%8A%A4%E5%A3%AB&typeall=1&suball=1&timescope=custom%3A' \
                   + start_time + '%3A' + end_time + '&Refer=g&page='
        frist_url = base_url + '1'
        response = requests.get(frist_url, headers=headers)
        root = etree.HTML(response.content)
        page_lists = root.xpath('//div[@class="m-page"]//ul/li')
        for j in range(1, len(page_lists) + 1):
            url = base_url + str(j)
            yield url


def get_per_response(url, headers):
    """
    根据每一页的url，获取其每一项的内容，开始解析
    :param url:
    :return:
    """
    response = requests.get(url, headers=headers)
    root = etree.HTML(response.content)
    articles = root.xpath('//div[@class="card-wrap"]')
    num = 1
    for article in articles:
        # 动态内容
        article_content = article.xpath('div/div/div/p[@class="txt"]/text()')
        article_content = "".join(article_content).replace(' ', '').replace('\n', '').strip()

        # 用户名称
        user_name = article.xpath('div//div[@class="content"]/div/div/a/@nick-name')
        user_name = user_name[0] if user_name else "无用户名"

        # 收藏、转发、评论、点赞人数
        # 发布时间
        try:
            repeat = article.xpath('//div[@class="card-act"]/ul/li[1]/a/text()')
            repeat = repeat[num]
            comment = article.xpath('//div[@class="card-act"]/ul/li[2]/a/text()')
            comment = comment[num]
            comment_url = article.xpath('//div[@class="from"]/a/@href')
            comment_url = "https:" + comment_url[num - 1]
            support = article.xpath('//div[@class="card-act"]/ul/li[3]/a//span[@class="woo-like-count"]/text()')
            support = support[num]
            # 时间
            publish_time = article.xpath('//div[@class="from"]/a[@target="_blank"]/text()')
            publish_time = publish_time[num].strip()
            num += 2
            # 秒
            try:
                if "秒" in publish_time:
                    publish_time = publish_time.replace("秒前", '').strip()
                    # 拿当前时间戳减去多少秒，然后转化成对应的日期
                    timestamp = time.time()
                    timestamp -= int(publish_time)
                    publish_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
                elif "分钟" in publish_time:
                    try:
                        publish_time = publish_time.replace("分钟前", '').strip().split(' ')[0]
                    except Exception as e:
                        publish_time = publish_time.replace("分钟前", '').strip()
                    timestamp = time.time()
                    timestamp -= int(publish_time) * 60
                    publish_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
                elif "今天" in publish_time:
                    now_time = time.localtime()
                    publish_time = publish_time.replace("今天", '').strip()
                    localtime = time.strftime("%Y-%m-%d", now_time)
                    publish_time = localtime + ' ' + publish_time
                if '月' in publish_time:
                    publish_time = publish_time.replace('月', '-')
                    publish_time = publish_time.replace('日', '')
                    if '年' in publish_time:
                        publish_time = publish_time.replace('年', '-')
                    else:
                        publish_time = str(time.localtime(time.time())[0]) + '-' + publish_time
                yield user_name, publish_time, article_content, repeat, comment, comment_url, support
            except ValueError as e:
                pass
        except IndexError as e:
            pass


def addZero(i):
    if i <= 9:
        key = '0' + str(i)
    else:
        key = str(i)
    return key


if __name__ == '__main__':
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Cookie": '_s_tentry=weibo.com; Apache=4283478381590.2246.1667119415906; SINAGLOBAL=4283478381590.2246.1667119415906; ULV=1667119415969:1:1:1:4283478381590.2246.1667119415906:; login_sid_t=2ee42ca686a88d2529e0e06390ae1743; cross_origin_proto=SSL; SSOLoginState=1667119464; SUB=_2A25OWkk4DeRhGeNH7FES-C3JyDWIHXVtpVdwrDV8PUJbkNANLXL-kW1NSp8dFFpnPmyshBwhqo5QVIarYUyOvAf4; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5YTJYqAmBSadnEgVI0oZn45NHD95Qf1KM0e0n0SKe4Ws4Dqcj1BcyEIPScIg4Lwg8E9FXt'
    }

    # row从1开始，每写入xls一行数据，row += 1
    year = int(input('请输入年：'))
    month = int(input('请输入月：'))
    row = 1
    # 创建excel对象
    xcl = Excel(year=year, month=month)
    days = calendar.monthrange(int(year), int(month))[1]
    for day in range(1, int(days)+1):
        str_time = str(year) + '-' + addZero(month) + '-' + addZero(day)
        for url in get_per_url(str_time):
            # 返回一个元组，这个元组包括每一条动态的数据
            for per_data in get_per_response(url, headers):
                xcl.write_data(row, per_data)
                row += 1
            xcl.save_excel_data(year, month)
