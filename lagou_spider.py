# -*- coding:utf-8 -*-
# time:2018-10-22

import requests
import random
import time
import pandas as pd
import matplotlib.pylab as plt
import jieba
from wordcloud import WordCloud

# 该爬虫爬取拉勾网用户想要查询的地区的python相关招聘信息,并且进行数据处理与分析.

# 获取请求结果
# kind 搜索关键字
# page 页码, 默认是1
def get_json(kind, city, page=1,):
    # post请求参数
    data = {
        'first':"true",
        'pn':page,
        'kd':kind
    }
    # 想要搜索的城市名称
    kw = {'city':city,'needAddtionalResult':'false'}

    user_agent_list = ['Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
                  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
                  'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
                  'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
                  'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201']


    user_agent = random.choice(user_agent_list)
    print('1:',user_agent)

    header = {
        'Host': 'www.lagou.com',
        'Referer': 'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=',
        'User-Agent': user_agent
    }
    print(header)

    # 设置代理
    proxies = [
        {'http': '140.143.96.216:80', 'https': '140.143.96.216:80'},
        {'http': '119.27.177.169:80', 'https': '119.27.177.169:80'},
        {'http': '221.7.255.168:8080', 'https': '221.7.255.168:8080'}
    ]

    # 请求的url
    # url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false'
    url = 'https://www.lagou.com/jobs/positionAjax.json?'
    #使用代理访问
    # response = requests.post(url, headers=header, data=param, proxies=proxies)
    response = requests.post(url, params=kw, headers=header, data=data)

    print(response.text)
    response.encoding='utf-8'

    if response.status_code == 200:
        response = response.json()
        # 请求响应中的positionResult 包括查询总数 以及该页的招聘信息(公司名、地址、薪资、福利待遇等...)
        # print response
        return response['content']['positionResult']
    return None



if __name__ == '__main__':
    # 默认先查询第一页的数据
    # kind = 'python'
    kind = input('请输入您想要查询的类型:')
    # 默认爬取的为全国信息.
    # city = '北京'
    city = input('请输入您想要查询的城市:')
    # 请求一次 获取总条数
    response_result = get_json(kind, city)
    # 招聘总条数
    total = response_result['totalCount']
    print('{}开发职位,招聘信息总共{}条.....'.format(kind, total))

    # 所有查询结果
    search_job_result = []

    # 拉钩网爬取30页面信息
    for i in range(1, 30):
        response_result = get_json(kind, city, page=i)
        # # 每次抓取完成后,暂停一会,防止被服务器拉黑
        time.sleep(15)
        #当前页的招聘信息
        page_kind_job = []
        for j in response_result['result']:
            kind_job = []
            # 公司全名
            kind_job.append(j['companyFullName'])
            # 公司简称
            kind_job.append(j['companyShortName'])
            # 公司规模
            kind_job.append(j['companySize'])
            # 融资
            kind_job.append(j['financeStage'])
            # 所属区域
            kind_job.append(j['district'])
            # 职称
            kind_job.append(j['positionName'])
            # 要求工作年限
            kind_job.append(j['workYear'])
            # 招聘学历
            kind_job.append(j['education'])
            # 薪资范围
            kind_job.append(j['salary'])
            # 福利待遇
            kind_job.append(j['positionAdvantage'])

            page_kind_job.append(kind_job)

        # 放入所有的列表中
        search_job_result += page_kind_job
        print(search_job_result)
        print('第{}页数据爬取完毕, 目前职位总数:{}'.format(i, len(search_job_result)))
        # 每次抓取完成后,暂停一会,防止被服务器拉黑
        time.sleep(15)

        df = pd.DataFrame(data=search_job_result,
                          columns=['公司全名', '公司简称', '公司规模', '融资阶段', '区域', '职位名称', '工作经验', '学历要求', '工资', '职位福利'])
        df.to_csv('lagou.csv', index=False, encoding='utf-8_sig')

    # ---------------数据分析--------------
    #剔除实习岗位的招聘、工作年限无要求或者应届生的当做0年处理、薪资范围需要计算出一个大概的值、学历无要求的当成大专
    # 读取数据
    df = pd.read_csv('lagou.csv', encoding='utf-8')
    # 数据清洗,剔除实习岗位
    df.drop(df[df['职位名称'].str.contains('实习')].index,inplace=True)
    # 由于CSV文件内的数据是字符串形式,先用正则表达式将字符串转化为列表,再取区间的均值
    pattern = '\d+'
    df['work_year'] = df['工作经验'].str.findall(pattern)
    print('work_year:', df['work_year'])
    # 数据处理后的工作年限
    avg_work_year = []
    # 工作年限
    for i in df['work_year']:
        # 如果工作经验为'不限'或应届毕业生',那么匹配值为空,工作年限为0
        if len(i) == 0:
            avg_work_year.append(0)
            # print('avg_work_year:', avg_work_year)
        # 如果匹配值为一个数值,那么返回该数值
        elif len(i) == 1:
            avg_work_year.append(int(''.join(i)))
        # 如果匹配值为一个区间,那么取平均值
        else:
            num_list = [int(j) for j in i]
            avg_year = sum(num_list)/2
            avg_work_year.append(avg_year)
    print('avg_work_year:',avg_work_year)
    df['工作经验'] = avg_work_year


    # 将字符串转化为列表,计算月平均薪酬,取区间差值的前25%，并且取整数比较贴近现实
    df['salary'] = df['工资'].str.findall(pattern)
    # 月薪
    avg_salary = []
    for k in df['salary']:
        int_list = [int(n) for n in k]
        avg_wage = int_list[0] + (int_list[1] - int_list[0]) / 4
        avg_salary.append(avg_wage)
    df['月工资'] = avg_salary

    # 将学历不限的职位要求认定为最低学历:大专\
    df['学历要求'] = df['学历要求'].replace('不限', '大专')

    df.to_csv('lagou_finall.csv', index=False, encoding='utf-8_sig')

    #-------------数据图形可视化--------------

    # 中文乱码的处理
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    #绘制薪资频率直方图
    plt.hist(df['月工资'])
    # plt.xlabel('工资 (千元)')
    plt.xlabel('salary(thousand yuan)')
    # plt.ylabel(u'频数')
    plt.ylabel('frequency')
    # plt.title(u"工资直方图")
    plt.title("salary histogram")
    plt.savefig('薪资.png')
    plt.show()

    #绘制公司分布饼状图
    count = df['区域'].value_counts()
    plt.pie(count, labels=count.keys(), labeldistance=1.4, autopct='%2.1f%%')
    plt.axis('equal')  # 使饼图为正圆形
    plt.legend(loc='upper left', bbox_to_anchor=(-0.1, 1))
    plt.savefig('公司分布.png')
    plt.show()

    #绘制学历要求直方图
    # {'本科': 666, '大专': 44, '硕士': 33, '博士': 1}
    dict = {}
    for i in df['学历要求']:
        if i not in dict.keys():
            dict[i] = 0
        else:
            dict[i] += 1
    index = list(dict.keys())
    print('index:',index)
    num = []
    for i in index:
        num.append(dict[i])
    print('num:',num)
    plt.bar(index, num, width=0.5)
    plt.savefig('学历要求.png')
    plt.show()


'''
    #绘制福利待遇词云图,将职位福利中的字符串汇总
    text = ''
    for line in df['职位福利']:
        text += line
        # 使用jieba模块将字符串分割为单词列表
    cut_text = ' '.join(jieba.cut(text))
    print('cut_text',cut_text)
    # color_mask = imread('cloud.jpg')  #设置背景图
    cloud = WordCloud(
        background_color='white',
        # 对中文操作必须指明字体
        font_path='hanyiqihei.ttf',
        # mask = color_mask,
        max_words=1000,
        max_font_size=100
    )
    cloud.generate_from_text(cut_text)

    # 保存词云图片
    cloud.to_file('word_cloud.jpg')
    plt.imshow(cloud)
    plt.axis('off')
    plt.show()
'''















