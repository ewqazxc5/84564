from math import *
from random import *


k = 3
iterations = 10

lines = open('samples.csv', 'r').readlines()
ps = []
for line in lines: 
  numbers = line.strip().split(',')
  ps.append(tuple(map(float, numbers)))

m = [None]*k
for i in range(k):
  m[i] = ps[randrange(len(ps))]

alloc = [None]*len(ps)

for n in range(iterations):
  for i in range(len(ps)):
    p = ps[i]
    d = [None] * k
    for di in range(k):
      mi = m[di]
      d[di] = sqrt((p[0]-mi[0])**2 + (p[1]-mi[1])**2 + (p[2]-mi[2])**2)
    alloc[i] = d.index(min(d))

  for i in range(k):
    alloc_ps = [p for j, p in enumerate(ps) if alloc[j] == i]
    sum0 = sum1 = sum2 = 0
    for a in alloc_ps:
      sum0 += a[0]
      sum1 += a[1]
      sum2 += a[2]
    new_mean=(sum0 / len(alloc_ps), sum1 / len(alloc_ps), sum2 / len(alloc_ps))
    m[i]=new_mean

for i in range(k):
  alloc_ps=[p for j, p in enumerate(ps) if alloc[j] == i]
  print("Cluster " + str(i) + " is centred at " + str(m[i]) + " and has " + str(len(alloc_ps)) + " points.")

  print(alloc_ps)

"""
from matplotlib import pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
for i in range(3):
  alloc_ps = [p for j, p in enumerate(ps) if alloc[j]==i]
  ax.scatter([a[0] for a in alloc_ps],[a[1] for a in alloc_ps],[a[2] for a in alloc_ps])
  plt.show()
"""
