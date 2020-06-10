# -*- coding:utf-8 -*-
import sys
import os
import tf_extractor

if __name__ == '__main__':
    try:
        # 主题抽取
        tf_extractor.extractTopics()
        # 读取topicPath
        with open('./topics.txt', 'r', encoding='utf-8') as f:
            topics = f.readlines()
        # 创建输出文件夹
        if not os.path.exists('./output/'):
            os.mkdir('./output/')
        tf_extractor.extractFacets(topics)
    except Exception as e:
        print('错误: ', e)
