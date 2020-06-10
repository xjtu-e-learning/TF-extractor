# -*- coding: utf-8 -*-
import os
import requests
from urllib import parse
from bs4 import BeautifulSoup


def __crawl(topic):
    facets = []
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36'
    headers = {'User-Agent': user_agent}
    response = requests.get('https://baike.baidu.com/item/' + parse.quote(topic), headers=headers)
    text = response.text
    if response.status_code == 200:
        with open('./tmp/' + topic + '/raw.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        soup = BeautifulSoup(text, 'html.parser')
        contents = soup.find('div', attrs={'class': 'lemma-catalog'})
        if contents:
            lis = contents.find_all('li', attrs={'class': 'level1'})
            for li in lis:
                facet = li.find('span', attrs={'class': 'text'}).get_text()
                if topic in facet:
                    index = facet.index(topic)
                    if index + len(topic) < len(facet) and facet[index + len(topic)] == '的':
                        facet = facet[index + len(topic) + 1:]
                    else:
                        facet = facet[index + len(topic):]
                    if facet == '':
                        continue
                facets.append(facet)

    return facets


def crawl(topics):
    # 是否存在文件夹
    if not os.path.exists('./tmp/'):
        os.mkdir('./tmp/')
    print('启动爬虫:')
    i = 0
    for topic in topics:
        topic = topic.strip()
        ## 如果构建过了
        if os.path.exists('./tmp/' + topic + '/'):
            i += 1
            continue
        os.mkdir('./tmp/' + topic + '/')
        facets = __crawl(topic)
        with open('./tmp/' + topic + '/facets.txt', 'w', encoding='utf-8') as f:
            f.writelines([f + '\n' for f in facets])
        i += 1
        print(str(int(i / len(topics) * 100)) + '%')
