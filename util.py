#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Author: nuoline@gmail.com
Date: 2020/11/21 16:03:39
"""
import sys
import math

#############################################################
##################### 日志相关处理 ##########################

g_debug  = sys.stderr
g_notice = sys.stderr

# 初始化日志
def init_log(log_file) :
    global g_debug, g_notice
    g_debug  = open(log_file+".dbg", "a")
    g_notice = open(log_file+".log", "a") 

# 输出更多较为细节的信息    
def debug(fmt, msg) :
    print >> g_debug, fmt%msg

# 输出处理到哪一步了
# 所有notice的信息也会打印到debug里
def notice(fmt, msg) :
    print >> g_notice, fmt%msg
    print >> sys.stderr, fmt%msg
    debug(fmt, msg)

#############################################################
##################### 常用的计算 ############################

def safe_div(a, b, s=1e-6) : return float(a)/max(float(b), s)

def range_equal(arr, start, end, val) :
    for i in range(start, end) : 
        if arr[i] != val : return False
    return True

def range_set(arr, start, end, val) :
    for i in range(start, end) : arr[i] = val

def round_list(data, round_num) :
    return [round(x, round_num) for x in data]

#############################################################
##################### 字符串相关处理 ########################

# 去除两个数组在首尾上的相同部分
def get_array_diff(a, b) :
    i, j = 0, len(a)-1
    p, q = 0, len(b)-1
    
    while i <= j and p <= q and a[i] == b[p]:
        i += 1
        p += 1
    
    while j >= i and q >= p and a[j] == b[q]:
        j -= 1
        q -= 1

    return i, j+1, p, q+1

# 计算两个片段在字级别上的diff
# note : 这个函数的性能不太行
def get_char_diff(a, b) :
    ua = a.decode('gb18030', 'ignore')
    ub = b.decode('gb18030', 'ignore')
   
    i, j, p, q = get_array_diff(ua, ub)
    
    a_diff = ua[i:j].encode('gb18030')
    b_diff = ub[p:q].encode('gb18030')

    return a_diff, b_diff 

# 把中文打散成单字
def split_chinese(s):
    char = []
    try:
        uni  = unicode(s, 'gbk')
        char = [w.encode('gbk') for w in uni]
    except:
        pass
      
    return char

#############################################################
###################### 文件处理相关 #########################

def load_data(file, col_num=0) :    
    data = []
    
    for line in open(file) :
        line = line.rstrip("\n")
        cols = line.split("\t")
        if col_num > 0 : 
            if len(cols) < col_num :
                notice("# ERROR : wrong line (%s)", line)
                continue
            data.append(cols[0:col_num])
        else :
            data.append(cols)

    return data

# feature name => id
def load_meta(input, format="name2id"):
  name2id = {}
  id2name = {}
  idx = 0

  for line in open(input) :
    name = line.rstrip("\n")
    if not name.startswith("#") :
      name2id[name] = idx 
      id2name[idx]  = name
      idx += 1

  if format=="name2id" : return name2id
  if format=="id2name" : return id2name
  return None

#############################################################
###################### 特征处理相关 #########################
# 分析目标特征的统计值
# fdata : (x, y)[]
# @return : 
#     x_list : 把样本按特征值从小到大分成若干个区间    
#     y_list : 每个区间里label的均值
#     n_list : 每个区间里的样本数
def analyse_feature(fdata, intervals=16, rmin=None, rmax=None) :
    x_list, y_list, n_list = [], [], []
    num = len(fdata) 
    
    if num <= 0 : return x_list, y_list, n_list 
  
    set_x = set()
    for x, y in fdata : set_x.add(x)
    
    # 如果是离散值特征, 则分割点不必计算
    if len(set_x) < 16 :
        x_list = sorted(set_x)
        y_list = [0] * len(x_list) 
        n_list = [0] * len(x_list)
        
        for x, y in fdata :
            p = 0
            for i in range(len(x_list)-1, -1, -1) :
                if x == x_list[i] :
                    p = i
                    break
            y_list[p] += y
            n_list[p] += 1
    else :
        fdata.sort(key=lambda x : x[0])
        xmin = fdata[0][0]
        xmax = fdata[-1][0]

        if rmin : xmin = max(xmin, rmin)
        if rmax : xmax = min(xmax, rmax)

        x_list = [xmin + (xmax-xmin)/intervals * i for i in range(intervals)]
        y_list = [0] * len(x_list)
        n_list = [0] * len(x_list)

        for x, y in fdata :
            if x > xmax or x < xmin : continue
            p = 0
            for i in range(len(x_list)-1, -1, -1) :
                if x >= x_list[i] :
                    p = i
                    break
            y_list[p] += y
            n_list[p] += 1

    for i in range(len(y_list)) :
        y_list[i] *= safe_div(1.0, n_list[i])
 
    return x_list, y_list, n_list

# 按列抽取出特征与对应的label
# feature => (x, y)*
def get_feature_label_pair(data, name2id) :
    result = {}

    for fname in name2id : result[fname] = []
    for row in data :
        query, word, rword, label = row[0], row[1], row[2], int(row[3])
        fv = row[4:]
        for fname, id in name2id.iteritems() :
            result[fname].append((float(fv[id]), label))

        if (len(fv)) != len(name2id) :
            notice("# error : wrong feature size, fv=%d, name2id=%d", (len(fv), len(name2id)))

    return result

#############################################################
######################## 指标计算 ###########################

class ErrorCount :
    def __init__(self) :
        self.total_ = 0
        self.pos_ = 0
        self.neg_ = 0
        self.r2r_ = 0
        self.r2w_ = 0
        self.w2r_ = 0
        self.w2w_ = 0
        self.loss_ = 0
        self.error_type_ = { (1,1):"r2r", (1,0):"r2w", (0,1):"w2r", (0,0):"w2w" }
    
    def Count(self, label, predict, belief) :
        self.total_ += 1
        
        if label == 1 : 
            self.pos_ += 1
            if predict == label : 
                self.r2r_ += 1
            else : 
                self.r2w_ += 1
            p = max(min(1, belief), 0)
            self.loss_ += math.log(p+1e-5)
        elif label == 0 :
            self.neg_ += 1
            if predict == label : self.w2w_ += 1
            else : self.w2r_ += 1
            p = max(min(1, 1-belief), 0)
            self.loss_ += math.log(p+1e-5)
        return self.error_type_[(label, predict)] 

    def total(self) : return self.total_

    def Summary(self, out) :
        print >> out, "# samples :"
        print >> out, "    %10s %10d"%("total", self.pos_+self.neg_)
        print >> out, "    %10s %10d %10.3f"%("positive", self.pos_, safe_div(self.pos_, self.pos_+self.neg_))
        print >> out, "    %10s %10d %10.3f"%("negative", self.neg_, safe_div(self.neg_, self.pos_+self.neg_))

        print >> out, "# error matrix :"
        print >> out, "    %10s %10s %10s"%("y/y'", 0, 1)
        print >> out, "    %10d %10d %10d"%(0, self.w2w_, self.w2r_)
        print >> out, "    %10s %10s %10s"%(1, self.r2w_, self.r2r_)

        print >> out, "# measure :"
        print >> out, "    %10s %10s %10s %10s"%("precision", "recall", "f-measure", "entropy")
        prec, recall = safe_div(self.r2r_, self.r2r_+self.w2r_), safe_div(self.r2r_, self.pos_)
        fmea = safe_div(2*prec*recall, prec+recall)
        ent  = safe_div(self.loss_, self.pos_ + self.neg_)
        print >> out, "    %10.3f %10.3f %10.3f %10.3f"%(prec, recall, fmea, ent)
