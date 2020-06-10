# -*- coding: utf-8 -*-
from shutil import copyfile
from .low_topic.low_topic import readJSONFile, userDict, getTFIDFResult, getPosseg
from .spider.baiduSpider import crawl
from .docx_filter.docx_filter import filter_docx

def extractTopics():
    # 读百度百科爬虫json文件并转换格式
    readJSONFile()
    # 获得分词外部词典
    userDict()
    # 计算tfidf结果
    getTFIDFResult()
    # 词性分析
    getPosseg()
    # TODO: 缺个步骤：把包含主题的xls文件改写成一个txt文件，每一行是一个主题

def extractFacets(topics):
    crawl(topics)
    filter_docx(topics)

    # 拷贝文件
    for topic in topics:
        topic = topic.strip()
        copyfile('./tmp/' + topic + '/' + 'facets_filter.txt', './output/' + topic + '.txt')
    pass
