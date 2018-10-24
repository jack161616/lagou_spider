# lagou_spider
该爬虫爬取拉勾网用户想要查询的地区的python相关招聘信息,并且进行数据处理与分析可视化。  

分析url时候，从网页源代码中我们并不能找到发布的招聘信息。但是在请求中我们看到这样一条POST请求：  
url：https://www.lagou.com/jobs/positionAjax.json?city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false  
因此，可以从该url获取招聘的相关json数据。  

采用post请求，Form Data有三个参数：  
first ： 是否首页  
pn：页码  
kd：搜索关键字    

后面就可以通过requests请求得到想要的json数据。
进行数据筛选，与可视化处理。

