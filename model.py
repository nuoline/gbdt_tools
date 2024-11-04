#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Author: nuoline@gmail.com
Date: 2021/11/21 16:03:39
"""
import sys
import os
kRoot = os.path.dirname(os.path.abspath(__file__))+"./"
sys.path += [kRoot+'/pylib']
import tree_model

class RandomForest :
    def __init__(self, model_path, meta = None) :
        self.model = tree_model.LoadModel(model_path)
        self.fs = self.LoadFeatureSelector(meta)

    # 假定meta里的特征是有序的, 且通过加#来删除特征
    def LoadFeatureSelector(self, meta):      
        fs = None
        
        if meta != None :
            fs = []  
            for line in open(meta) :
                if line.startswith('#') : 
                    fs.append(0)  
                else :
                    fs.append(1)

        return fs

    def SelectFeature(self, fv) :
        if not self.fs : 
            return fv   
        else :
            if len(fv) != len(self.fs) : 
                raise Exception("# ERROR : fv.size != fs.size %d vs %d"%(len(fv), len(self.fs)))
            sfv = []
            for i in range(len(fv)) :
                if self.fs[i] == 1 : 
                    sfv.append(fv[i])
            return sfv        

    def Predict(self, fv):
        features = map(float, fv)

        features = self.SelectFeature(features)

        result = tree_model.OnlineTesting(self.model, features)

        # 这里是为了处理gbdt的[0,1]的连续值
        if result[0] > 0.48 :
            result[0] = 1 
        else :
            result[0] = 0

        return (int(result[0]), result[1])

    def Destroy(self) :
        tree_model.ReleaseModel(self.model)
