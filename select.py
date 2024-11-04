#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Author: nuoline@gmail.com
Date: 2020/11/21 16:03:39
"""
import sys
from optparse import OptionParser

# name => id
def load_flist(input) :
  idx = 0
  fid = {}

  for line in open(input) :
    fname = line.rstrip("\n")
    fid[fname] = idx
    idx += 1

  return fid

def load_active_feature(input, fid) :
  active_set = set()

  for line in open(input) :
    fname = line.rstrip("\n")
    if fname.startswith("#") : continue
    id = fid[fname]
    active_set.add(id)

  return active_set 

def extract_active_feature(fv, aid) :
  result = []
  for i in range(len(fv)) :
    if i in aid : result.append(fv[i])
  return result

def select(aid, fi, fo, fv_index) :
  fv_start = int(fv_index)
  for line in fi:
    row = line.rstrip("\n").split('\t')
    fv = row[fv_start:]
    fv = extract_active_feature(fv, aid)

    print >> fo, '\t'.join(row[:fv_start] + fv)

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-m", "--flist", dest="flist")
  parser.add_option("-a", "--active_flist", dest="active_flist")
  parser.add_option("-f", "--fv_indxi", dest="fv_index")
  (options, args) = parser.parse_args()

  if not options.flist or not options.active_flist or not options.fv_index :
    parser.print_help()
    sys.exit(-1)

  fid = load_flist(options.flist)
  aid = load_active_feature(options.active_flist, fid)

  select(aid, sys.stdin, sys.stdout, options.fv_index)
