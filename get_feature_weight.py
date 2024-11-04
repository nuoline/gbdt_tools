#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Author: nuoline@gmail.com
Date: 2020/12/28 16:03:39
"""

import sys
import os
import re
import util

kModelPath = "./exp/tree_model"
kActiveMeta = "./exp/active.meta"

def feature_weight_analysis(data_path, model_path = None, active_meta = None):
    if model_path == None:
        model_path = kModelPath
    if active_meta == None:
        active_meta = kActiveMeta

    debugger_filename = './feature_analysis'
    debugger_output = os.popen(' '.join([debugger_filename, model_path, data_path]))
   
    feature_weight = []
    r = re.compile('[ ]+')
    for line in debugger_output:
        fields = r.split(line.strip())
        if len(fields) == 3:
            feature_weight.append(fields)
    
    id2name = util.load_meta(active_meta, "id2name")

    for entry in feature_weight:
        try:
            fname = id2name[int(entry[0])]
        except:
            fname = "Unknown Feature:" + entry[0]
        entry[0] = fname

    debugger_output.close()
    return feature_weight

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print >> sys.stderr, "Usage: " + sys.argv[0] + " <training data file> <model file> <active meta>"
        exit(255)
  
    data_path = sys.argv[1]
    model_path = sys.argv[2]
    active_path = sys.argv[3]
    feature_weight = feature_weight_analysis(data_path, model_path, active_path)

    print "%-20s %-15s %-15s" % ("Feature Name", "Feature Weight", "Feature Used Freqency")

    for item in feature_weight:
        print "%-20s %-15s %-15s" % (item[0], item[1], item[2])
