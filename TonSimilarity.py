'''
Author: LIU Hanwen
Email: liu.hanwen@foxmail.com
Github: https://github.com/liu-hanwen/
Created Date: April 22, 2018
'''

from pypinyin import pinyin as py_pinyin
from pypinyin import Style
import os
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import Levenshtein
import sijiao_dict
import pickle

boost_dict = None

try:
    with open('./ssc_ton.pkl', 'rb') as f:
        boost_dict = pickle.load(f)
except:
    boost_dict = {}

d = sijiao_dict.dic

for key in d:
    d[key] = np.array([int(ch) for ch in d[key]])

def pinyin(ch):
    return py_pinyin(ch, style=Style.TONE3, heteronym=True)[0]

def ssc(ch):
    return {"pinyin": pinyin(ch)}

def similarity(ch1, ch2, tone=True, shape=False, wpy=0.5, wst=0.1, wsj=0.2, wmatrix=0.2):
    if ch1 in boost_dict:
        ssc1 = boost_dict[ch1]
    else:
        ssc1 = ssc(ch1)
        boost_dict[ch1] = ssc1

    if ch2 in boost_dict:
        ssc2 = boost_dict[ch2]
    else:
        ssc2 = ssc(ch2)
        boost_dict[ch2] = ssc2

    # pinyin similarity com
    # hputing
    py1 = ssc1['pinyin']
    py2 = ssc2['pinyin']
    # print(py1,py2)
    py_dict = {'ch': 'c', 'zh': 'z', 'sh': 's', 'ing': 'in', 'eng': 'en', 'ang': 'an'}

    py1 = ','.join(py1)
    py2 = ','.join(py2)
    for key in py_dict:
        py1.replace(key, py_dict[key])
        py2.replace(key, py_dict[key])

    py1 = py1.split(',')
    py2 = py2.split(',')

    min_distance = 5
    max_len = 0
    for py1_item in py1:
        if len(py1_item)>max_len:
            max_len = len(py1_item)
        for py2_item in py2:

            if len(py2_item)>max_len:
                max_len = len(py2_item)

            temp_d = Levenshtein.distance(py1_item,py2_item)
            if temp_d < min_distance:
                min_distance = temp_d
    py_similarity = 1-(min_distance/max_len)
    return py_similarity

print(similarity('候','侯'))