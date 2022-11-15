import requests
import xlrd
import json
import xlwt
import os

# 取消服务器代理，直接由本机发送请求
os.environ['NO_PROXY'] = 'weibo.com'

"""
获取评论数据
:param url: 评论内容url
:param headers: 评论内容请求头
:return 评论数据集
"""
def get_response(url,headers):
    try:
        # 发送get请求，获取response对象
        response = requests.get(url=url,headers=headers)
        # 将response对象内的text装载成json对象
        data = json.loads(response.text)
        # 返回评论文本集
        for item in data['data']:
            text = item['text']
            yield text
    except BaseException as be:
        pass
"""
打开execl文件，获取评论内容页面的url
:param execl_path: execl文件的路径
:return 返回评论内容url、行号
"""
def open_xls(execl_path):
    # 打开execl文件
    data = xlrd.open_workbook(execl_path+'.xlsx')
    # 获取文件的第一页工作簿
    sheet = data.sheets()[0]
    # 获取第四列的值
    col_list = sheet.col_values(4)
    for i in range(1, len(col_list)):
        # 筛选出第四列不是评论的值
        if col_list[i].strip() != '评论':
            # 获取当前行第5列存放的评论url
            url = sheet.cell(i, 5).value
            yield (url,i+1)

if __name__ == '__main__':
    # 请求头（后续需要更新使用者的请求头）
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Cookie": '_s_tentry=weibo.com; Apache=4283478381590.2246.1667119415906; SINAGLOBAL=4283478381590.2246.1667119415906; ULV=1667119415969:1:1:1:4283478381590.2246.1667119415906:; login_sid_t=2ee42ca686a88d2529e0e06390ae1743; cross_origin_proto=SSL; SSOLoginState=1667119464; SUB=_2A25OWkk4DeRhGeNH7FES-C3JyDWIHXVtpVdwrDV8PUJbkNANLXL-kW1NSp8dFFpnPmyshBwhqo5QVIarYUyOvAf4; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5YTJYqAmBSadnEgVI0oZn45NHD95Qf1KM0e0n0SKe4Ws4Dqcj1BcyEIPScIg4Lwg8E9FXt'
    }
    execl_path = input('请输入execl名：')
    # 生成execl对象，并穿件工作薄
    work_book = xlwt.Workbook('utf-8')
    excel_Worksheet = work_book.add_sheet('评论内容', cell_overwrite_ok=True)
    row_id = 0
    # 遍历每行博文数据
    for (url,row) in open_xls(execl_path):
        try:
            str = url.split('m/')[1].split('/')
            # 获得微博博主的uid
            uid = str[0]
            # 获取博主的id
            id = str[1].split('?')[0]
            # 生成评论实际的url
            real_url = url = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id=' \
          +id+'&is_show_bulletin=2&is_mix=0&count=10&uid='+uid
            for text in get_response(real_url,headers):
                excel_Worksheet.write(row_id, 0, text)
                excel_Worksheet.write(row_id, 1, row)
                work_book.save(execl_path + '_评论.xls')
                row_id += 1
        except BaseException as be:
            pass
