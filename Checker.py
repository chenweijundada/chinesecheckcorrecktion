'''
Author: LIU Hanwen
Email: liu.hanwen@foxmail.com
Github: https://github.com/liu-hanwen/
Created Date: April 28, 2018
'''
import pandas as pd
import pickle
from multiprocessing import Pool, Pipe
import jieba
# import CharSimilarity
import kenlm
import itertools
import sijiao_dict

'''参数'''
SIMI_DIC_PATH = './ssc_ton.pkl' # 相近字字典文件路径
LANG_MODEL_PATH = './text.bin' # 语言模型文件路径
VOCAB_PATH = '../data/weibo_contents_words.set'
MAX_MAYBE_WRONG_SIZE = 6 # 错字窗口最大值
N_GRAM = 3
SIMI_THRESHOLD = 0.5 # 超过阈值的相近字就会被匹配
TOP_N_CANDIDATE = 2

'''常见中文字表'''
# ch_list = list(CharSimilarity.sijiao_dict.dic.keys())
ch_list = list(sijiao_dict.dic.keys())

'''过滤字表'''
ignore_list = "的你我了就"

'''加载形近值字表simi_dic[word[i]][fixed_word[i]]))'''


simi_dic = { '等' : {'等':3,'灯':3},'侯' : {'好':3,'厚':3},'多' : {'躲':2,'夺':2},'是' :{'时':1,'食':1},'我': {'喔':5}}
# with open(SIMI_DIC_PATH, 'rb') as f:fix3 = correct_core('我已经等后多是。')
#     simi_dic = pickle.load(f)我已经等猴多时了。')

'''加载词汇表'''
# vocab_dic1  =  [['阿达是否'],['大法师福建噢'],['等候多是'],['等候的是'],[['等','候','多','是'],['等候多是'],['等后多时'],['等后多是']]]
vocab_dic  =  [['阿'],['等'],['多是'],['候的是'],[['等','侯','多','是'],['等','好','躲','时'],['灯','厚','夺','食']]]


# vocab_dic  =  { 1 : '我',2 : '你',3 : '撒',4 :'老',5: '把'}
# with open(VOCAB_PATH, 'rb') as f:
#     vocab_dic = pickle.load(f)

'''加载语言模型'''
lang_model = kenlm.LanguageModel(LANG_MODEL_PATH)

print('PREPROCESSING DONE!')

def substr(text):
    if len(text)==1:
        # print(" 1enis1 is %s" % (text))
        yield text
    else:

        yield [''.join(text)]
        for i in range(1, len(text)):
            left = [''.join(text[:i])]
            # print(" sub 前-left is %s" % (left))
            right = text[i:]
            for sub in substr(right):
                # print(" sub 后 -left is %s" % (left))
                # print(" sub 后 -right is %s" % (right))
                # print(" sub 后 -left+sub  is %s" % (left+sub))

                yield left + sub

def seek4simi(word):
    l = len(word)
    # print('word是%s' % word)
    # print(" l是%d " % (l))
    simi_value = 0.5
    not_in_dic_flag = False
    # print(" vocab4是%s" % (vocab_dic[4]))
    for fixed_word in vocab_dic[l]:
        # print('这是vocab_dict%s' % vocab_dic[l])
        #
        # print(" 这是fixeword 是 %s" % (fixed_word))
        # fixed_word = '等好躲时'

        for i in range(l):

            # print(word[i])

            try:
                if word[i] == fixed_word[i]:
                    # print(" fixe_word 是 %s" % (fixed_word))
                    # print(" word 是 %s" % (word))
                    #
                    # print(" fixe_word[i]  是 %s" % (fixed_word[i]))
                    # print(" word[i] 是 %s" % (word[i]))

                    simi_value += 1.0
                    # print(111111111)
                else:
                    # print(22222222)

                    str1 = '%s' % (word[i])
                    # print('这是103的数据%s' % str1)
                    str2 = '%s' % (fixed_word[i])
                    # print('这是121的数据%s' % str2)
                    #
                    # print('重要104%s103hang' % simi_dic[str1])
                    # print('重要105%s104hang' % simi_dic[str1][str2])
                    simi_value += simi_dic[str1][str2]

            except KeyError:
                not_in_dic_flag = True
                # print(not_in_dic_flag)
                break
        if not not_in_dic_flag:

            if simi_value / l > SIMI_THRESHOLD:
                # print(" 130 fixed_word is %s" % (fixed_word))
                # print(" 131 simi_value is %s" % (simi_value))
                fixed_word = ("".join(fixed_word))
                fixed_word = '%s' % fixed_word
                (simi_value) = simi_value / l


                yield fixed_word, simi_value
            else:
                # print(" 135simi_value is %s" % (simi_value))
                pass
            # print(" 137 simi_value is %s" % (simi_value))
            simi_value = 0.5

        else:
            not_in_dic_flag = False
            # print(" 142 simi_value is %s" % (simi_value))


def correct_algo(singletons, text):
    if len(singletons) == 1:
        print(888888)
        return text[singletons[0]]
    maybe_wrong = [text[idx] for idx in singletons]
    prefix = [text[idx] for idx in range(singletons[0] - N_GRAM + 1, singletons[0]) if idx >= 0]
    prefix = "".join(prefix)
    boost_dic2 = {'等侯多是': []}
    candidates = maybe_wrong
    candidate = candidates
    wrong_word = ("".join(candidates))
    ret = {}

    # print('%s 44444' % wrong_word)

    # for candidate in candidates:
    boost_dic = {'等侯多是': {}}
    boost_dic2 = {'等侯多是': []}
    ret = []


    for fixed_word, simi_value in seek4simi(wrong_word):
        # print('%s 156999999' % wrong_word)
        wrong_word = "'%s'" % wrong_word
        # print('%s 158999999' % wrong_word)
        # print('%s 159999999' % simi_value)

        boost_dic['等侯多是'][fixed_word] = simi_value
        boost_dic2['等侯多是'].append(simi_value)

        # print('这是161%s'%boost_dic)
        # print('%s161boos_dic[wrong_word]'%boost_dic[wrong_word])
        # boost_dic[wrong_word][fixed_word] = simi_value
    print('zheshi168%s'%boost_dic)
    boost_dic2['等侯多是'] = pd.Series(boost_dic2['等侯多是'])
    print('zhesh169i%s'%boost_dic2)
    fixed_products = boost_dic2['等侯多是'].nlargest(2).index.tolist()
    print('paixu%s'%fixed_products)
    b = [key for key, value in boost_dic['等侯多是'].items()]
    # print('zheshi b ')

    for fixed_product in fixed_products:

        # print(fixed_product)

        ll = lang_model.score(prefix + b[fixed_product])
        ret.append(ll)
    ret = pd.Series(ret)

    print('zheshi retpaixu%s'%ret)
    chuli =  ret.nlargest(1).index.tolist()
        # print('zheshi chuli %s'%chuli)
    chuli = chuli[0]
    chuli =  fixed_products[chuli]
    return b[chuli]
        # ret[''.join(list(fixed_product))] = lang_model.score(' '.join(prefix + b[fixed_product]))

    # print('wenzi%s'%b)

    # print('这是165%s' % boost_dic2[wrong_word])
    # print('这是165%s' % type(boost_dic2[wrong_word]))

    # fixed_products = boost_dic2['等侯多是'].nlargest(2).index.tolist()
    # print('zehshipaixu%s'%fixed_products)

    # for fixed_product in fixed_products:
    # print('prefix is %s'%prefix)
    #
    # ret[''.join(list(fixed_product))] = lang_model.score(' '.join(prefix + [''.join(list(fixed_product))]))



    # ret = pd.Series(ret)
    # return ret.nlargest(TOP_N_CANDIDATE).index.tolist()

def correct_core(text):
    singletons = [] # Storing singletons index
    text_splited = list(jieba.cut(text+'。', HMM = False))
    for word_index, word in enumerate(text_splited):
        if len(word)==1: # Singleton?
            if word in ignore_list or word not in ch_list or len(singletons)>MAX_MAYBE_WRONG_SIZE: # Frequent?
                if len(singletons)!=0:
                    newWord = correct_algo(singletons, text_splited)
                    # print(11111)
                    yield newWord
                if word_index!=len(text_splited) - 1:
                    yield word
                singletons = []
            else:
                singletons.append(word_index)
                # print(666666)
        else:
            if len(singletons)!=0:
                print(7777777)
                newWord = correct_algo(singletons, text_splited)
                yield newWord
            if word_index!=len(text_splited) - 1:
                print(11111)
                yield word
            singletons = []

fix3 = correct_core('我已经等侯多是。')

for word in fix3:
    print(word)
# answer = ''
# for word in fix:
#     if type(word) == list:
#         answer += word[0]
#     else:
#         answer += word
# print(222222)
# print(answer)
