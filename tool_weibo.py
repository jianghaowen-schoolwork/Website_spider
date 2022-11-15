# coding:utf-8
import xlwt

"""
把数据写入excel的工具类
"""


class Excel(object):

    # 读取数据
    def __init__(self,year,month):
        # 创建工作簿
        self.work_book = xlwt.Workbook('utf-8')

        # 创建一个excel表
        self.excel_Worksheet = self.work_book.add_sheet('微博用户动态', cell_overwrite_ok=True)

        # 创建第一行 标题
        self.rowTitle = ['用户名', '发布时间', '发布内容', '转发数', '评论数', '评论博文链接', '点赞数']

        # 把第一行写入表格
        for i in range(0, len(self.rowTitle)):
            self.excel_Worksheet.write(0, i, self.rowTitle[i])
        self.save_excel_data(year=year,month=month)\

    # 写入数据
    def write_data(self, row, movie_data_list):

        # 把电影数据写入表格
        for i in range(0, len(self.rowTitle)):
            self.excel_Worksheet.write(row, i, movie_data_list[i])

    def save_excel_data(self, year, month):
        # 这个保存是在建立一个工作簿那个对象进行保存的
        path = 'weibo_' + str(year) + '年_' + str(month) + '月_护士.xls'
        self.work_book.save(path)
