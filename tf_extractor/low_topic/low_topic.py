# coding:utf-8
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import jieba
import docx
import codecs
import xlrd
import xlwt
import json
import jieba.posseg as pseg


def readConfig(key):
    with open('./config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config.get(key, None)


# 百度百科爬虫结果json文件路径
jsonFile = readConfig('jsonFile')

# 将爬虫结果json文件内容转存到的excel文件路径
excelFile = readConfig('excelFile')

# 根据爬虫主题结果生成的主题外部词典路径
dictFile = readConfig('dictFile')

# 合同法文档集存放路径（文档集需要docx格式，且命名为从0开始的顺序文档，如0.docx文档）
documentFile = readConfig('documentFile')

# 合同法文档集数量 （从0开始算，0.docx为第0个文档）（其实可以按文档集数量-1的方式计算）
documentNum = readConfig('documentNum')

# 根据文档集计算主题tfidf值的文件路径
resultAfterIFIDF = readConfig('resultAfterIFIDF')

# 进行词性分析后的文件路径，最终的主题
resultAfterPOS = readConfig('resultAfterPOS')


def readJSONFile():
    # 读百度百科爬虫json结果文件，存放到excel文件中，方便阅读
    # 创建excel工作表
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')

    # 设置表头
    worksheet.write(0, 0, label='title')
    worksheet.write(0, 1, label='url')

    # 读取json文件
    with open(jsonFile, 'r', encoding='UTF-8') as f:
        data = json.load(f)

    # 将json字典写入excel
    # 变量用来循环时控制写入单元格，感觉有更好的表达方式
    val1 = 1
    val2 = 1
    for list_item in data:
        for key, value in list_item.items():
            if key == "title":
                worksheet.write(val1, 0, value)
                val1 += 1
            elif key == "url":
                worksheet.write(val2, 1, value)
                val2 += 1
            else:
                pass
    # 保存
    workbook.save(excelFile)


def userDict():
    # 根据百度百科爬虫结果，制定分词外部词典
    userDictFile = codecs.open(dictFile, 'w', 'utf-8')
    excel_path = excelFile
    excel = xlrd.open_workbook(excel_path, encoding_override="utf-8")
    # 返回所有Sheet对象的list
    all_sheet = excel.sheets()[0]
    # print(all_sheet)
    rows = all_sheet.nrows

    wordSet = []
    for i in range(1, rows):
        words = all_sheet.cell(i, 0).value
        if words not in wordSet:
            wordSet.append(words)
            userDictFile.write(words)
            userDictFile.write('\n')

    userDictFile.close()


def getUserDict():
    # 获得外部词典的字典形式列表并返回，用于计算tfidf
    excel_path = excelFile
    excel = xlrd.open_workbook(excel_path, encoding_override="utf-8")
    # 返回所有Sheet对象的list
    all_sheet = excel.sheets()[0]
    # print(all_sheet)
    rows = all_sheet.nrows
    dict = {}
    wordSet = []
    index = 0
    for i in range(1, rows):
        words = all_sheet.cell(i, 0).value
        if words not in wordSet:
            wordSet.append(words)
            dict[words] = index
            index += 1
    return dict


def getTFIDFResult():
    jieba.load_userdict(dictFile)  # 加载外部 用户词典

    text = ""
    # a = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19']
    # a=['0','1']
    for i in range(documentNum):
        txt = documentFile + str(i) + ".docx"
        file = docx.Document(txt)
        for p in file.paragraphs:
            text += p.text
        # with open(txt, 'r', 'utf-8') as f:
        #     for line in f:
        #         text += line

    sentences = text.split()
    sent_words = [list(jieba.cut(sent0)) for sent0 in sentences]
    document = [" ".join(sent0) for sent0 in sent_words]
    print('词料：', document)
    print('\n')

    vocabulary = getUserDict()
    tfidf_model = TfidfVectorizer(vocabulary=vocabulary).fit(document)
    # 得到语料库所有不重复的词
    feature = tfidf_model.get_feature_names()
    print('feature', feature)
    print('\n')
    # ['一切', '一条', '便是', '全宇宙', '天狗', '日来', '星球']
    # 得到每个特征对应的id值：即上面数组的下标
    print('vocabulary', tfidf_model.vocabulary_)
    print('\n')
    # {'一条': 1, '天狗': 4, '日来': 5, '一切': 0, '星球': 6, '全宇宙': 3, '便是': 2}

    # 每一行中的指定特征的tf-idf值：
    sparse_result = tfidf_model.transform(document)
    # print(sparse_result)

    # 每一个语料中包含的各个特征值的tf-idf值：
    # 每一行代表一个预料，每一列代表这一行代表的语料中包含这个词的tf-idf值，不包含则为空
    weight = sparse_result.toarray()

    # 构建词与tf-idf的字典：
    feature_TFIDF = {}
    for i in range(len(weight)):
        for j in range(len(feature)):
            # print(feature[j], weight[i][j])
            if feature[j] not in feature_TFIDF:
                feature_TFIDF[feature[j]] = weight[i][j]
            else:
                feature_TFIDF[feature[j]] = max(feature_TFIDF[feature[j]], weight[i][j])
    # print(feature_TFIDF)
    # 按值排序：
    # print('TF-IDF 排名前十的：')
    featureList = sorted(feature_TFIDF.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    # 写入excel
    # 创建excel工作表
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')

    # 设置表头
    worksheet.write(0, 0, label='title')
    worksheet.write(0, 1, label='score')
    worksheet.write(0, 2, label='frequency')
    # 变量用来循环时控制写入单元格，感觉有更好的表达方式
    val1 = 1
    val2 = 1
    val3 = 1

    for i in range(1, len(featureList)):
        if text.count(str(featureList[i][0])) > 0 and featureList[i][1] > 0:  ##过滤掉在文档集中出现次数为0的主题
            worksheet.write(val1, 0, str(featureList[i][0]))
            val1 += 1
            worksheet.write(val2, 1, featureList[i][1])
            val2 += 1
            worksheet.write(val3, 2, text.count(str(featureList[i][0])))
            val3 += 1
        # with open('结果存放11.txt', 'a') as file_handle:  # .txt可以不自己新建,代码会自动新建
        #     file_handle.write(str(featureList[i][0]))  # 写入
        #     file_handle.write(':')
        #     file_handle.write(str(featureList[i][1]))
        #     file_handle.write('\n')  # 有时放在循环里面需要自动转行，不然会覆盖上一条数据
        #     if i < 21:
        #         print(featureList[i][0], featureList[i][1])
        # print(featureList[i][0], featureList[i][1])

    # 保存最终主题的tfidf结果
    workbook.save(resultAfterIFIDF)


def getPosseg():
    # 对主题结果进行词性判断
    read_excel_path = resultAfterIFIDF
    excel = xlrd.open_workbook(read_excel_path, encoding_override="utf-8")

    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')

    # 设置写的文件的表头
    worksheet.write(0, 0, label='title')
    worksheet.write(0, 1, label='score')
    worksheet.write(0, 2, label='frequency')
    worksheet.write(0, 3, label='pos')

    # 返回所有Sheet对象的list
    all_sheet = excel.sheets()[0]
    # print(all_sheet)
    rows = all_sheet.nrows

    val = 1
    for i in range(1, rows):
        w = all_sheet.cell(i, 0).value
        score = all_sheet.cell(i, 1).value
        f = all_sheet.cell(i, 2).value

        nounNum = 0
        adjNum = 0
        tempwords = pseg.cut(w)  ###这块好像有点问题，jieba没有成功分词，不知道为什么，另外一个函数就正常分词了
        for word in tempwords:
            if (word.flag == 'n' or word.flag == 'vn'):
                nounNum += 1
            if (word.flag == 'a'):
                adjNum += 1
        if (nounNum < 1 and adjNum < 1):
            print("noun: ", w, " nounNum: ", str(nounNum), " adjNum: ", str(adjNum))
            continue
        if (len(w) <= 2):
            print("adj: ", w)
            continue

        worksheet.write(val, 0, w)
        worksheet.write(val, 1, score)
        worksheet.write(val, 2, f)
        col = 3
        words = pseg.cut(w)
        for word in words:
            worksheet.write(val, col, word.flag)
            col += 1
        val += 1

    workbook.save(resultAfterPOS)
