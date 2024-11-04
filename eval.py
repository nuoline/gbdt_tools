#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Author: nuoline@gmail.com
Date: 2020/12/21 16:03:39
"""
import sys
from optparse import OptionParser
import model 
import util

def eval(ml, input, output, fv_index):
    fvindx = int(fv_index)
    ##data = util.load_data(input)
    counter = util.ErrorCount()
    stat = open(output+".stat", "w")
    out  = open(output+".eval", "w")

    for line in open(input, 'r') :
        row = line.strip().split('\t')
        if len(row) < fvindx :
            continue
        qry_info = row[0:fvindx]
        label = int(row[fvindx - 1])
        fv = row[fvindx:]

        predict, belief = ml.Predict(fv)
        err = counter.Count(label, predict, belief)

        print >> out, '\t'.join(qry_info + map(str, [predict, belief] + fv))

    counter.Summary(stat)

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-m", "--model",  dest="model")
  parser.add_option("-i", "--input",  dest="input")
  parser.add_option("-o", "--output", dest="output")
  parser.add_option("-f", "--fv_indxi", dest="fv_index")
  (options, args) = parser.parse_args()

  if not options.input or not options.output or not options.model or not options.fv_index:
    parser.print_help()
    sys.exit(-1)

  rf = model.RandomForest(options.model)
  eval(rf, options.input, options.output, options.fv_index)
