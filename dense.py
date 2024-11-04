#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Author: nuoline@gmail.com
Date: 2020/11/21 16:03:39
"""
import sys
from optparse import OptionParser

def transfer(fi, fo, fv_index) :
  fv_in = int(fv_index)
  for line in fi:
    row = line.rstrip("\n").split('\t')
    if len(row) < fv_in :
        continue
    label = row[fv_in - 1]
    fv = row[fv_in:]

    val = []
    i = 0 
    for v in fv:
      i += 1
      val.append('%s:%s' % (i, v))

    print >> fo, ' '.join([label] + val)

if __name__ == '__main__':
  fv_index = sys.argv[1]
  transfer(sys.stdin, sys.stdout, fv_index)
