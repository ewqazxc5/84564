from math import *
from random import *

import numpy as np

"""
ps:  a list of points (as tuples)
"""
def cluster(ps, iterations = 10):
  # the number of clusters = 3
  k = 3
  m = [None]*k
  for i in range(k):
    m[i] = ps[randrange(len(ps))]

  alloc = np.zeros(len(ps), dtype=int)
  ps = np.array(ps)

  for n in range(iterations):
    for i in range(len(ps)):
      p = np.array(ps[i])
      mp = np.array(m)
      d = (mp-p)**2
      d = np.sum(d, axis = 1)
      alloc[i] = np.argmin(d)

    for i in range(k):
      alloc_ps = ps[alloc == i]
      sum = np.sum(alloc_ps, axis = 0)
      m[i] = sum/len(alloc_ps)
  return m, alloc.tolist()

import argparse
import sys

filename = 'samples.csv'
iters = 10
if len(sys.argv) > 1:
  parser = argparse.ArgumentParser()
  parser.add_argument('filename')
  parser.add_argument("-I", "--iters", type=int, help="iterations.")

  list = sys.argv
  args = parser.parse_args()
  if args.filename is not None:
    filename = args.filename
  if args.iters is not None:
    iters = args.iters

lines = open(filename, 'r').readlines()
ps = []
for line in lines: 
  numbers = line.strip().split(',')
  ps.append(tuple(map(float, numbers)))

m, alloc = cluster(ps, iters)
k = 3
for i in range(k):
  alloc_ps=[p for j, p in enumerate(ps) if alloc[j] == i]
  print("Cluster " + str(i) + " is centred at " + str(m[i]) + " and has " + str(len(alloc_ps)) + " points.")

  #print(alloc_ps)


