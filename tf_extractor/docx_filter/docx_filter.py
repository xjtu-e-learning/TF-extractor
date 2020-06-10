# -*- coding: utf-8 -*-
import docx
import os
import json


def readConfig(key):
    with open('./config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config.get(key, None)


def read_docx(docpath):
    fullText = []
    doc = docx.Document(docpath)
    paras = doc.paragraphs
    for p in paras:
        fullText.append(p.text)
    return '\n'.join(fullText)


def filter_docx(topics):
    # 每一个文档的内容是数组中的元素
    doc_contents = []
    for root, dirs, files in os.walk(readConfig('documentFile')):
        for filename in files:
            doc_contents.append(read_docx(os.path.join(root, filename)))
    # 分段
    para_contents = []
    for doc in doc_contents:
        para_contents.extend(doc.split('\n'))
    para_contents = list(filter(lambda s: s and s.strip(), para_contents))

    print('过滤中:')
    i = 0
    for topic in topics:
        i += 1
        topic = topic.strip()
        fs = []
        with open('./tmp/' + topic + '/facets.txt', 'r', encoding='utf-8') as f:
            facets = [facet.strip() for facet in f.readlines()]
            # 全文过滤
            # for facet in facets:
            #     for doc_content in doc_contents:
            #         if facet in doc_content:
            #             fs.append(facet + '\n')
            #             break

            # 逐段落过滤
            # for facet in facets:
            #     for para in para_contents:
            #         if facet in para and topic in para:
            #             fs.append(facet + '\n')
            #             break

            # 间隔段落过滤
            gap = 20
            for facet in facets:
                for index in range(0, len(para_contents) - gap):
                    tmp = '\n'.join(para_contents[index: index + gap])
                    if facet in tmp and topic in tmp:
                        fs.append(facet + '\n')
                        break

        with open('./tmp/' + topic + '/facets_filter.txt', 'w', encoding='utf-8') as f:
            f.writelines(fs)
        print(str(int(i / len(topics) * 100)) + '%')
