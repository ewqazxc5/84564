from math import *
from random import *


k = 3
iterations = 10

lines = open('samples.csv', 'r').readlines()
ps=[]
for line in lines: ps.append(tuple(map(float, line.strip().split(','))))

m=[ps[randrange(len(ps))], ps[randrange(len(ps))], ps[randrange(len(ps))]]

alloc=[None]*len(ps)
n = 0
while n < iterations:
  for i in range(len(ps)):
    p=ps[i]
    d=[None] * k

    d[0]=sqrt((p[0]-m[0][0])**2 + (p[1]-m[0][1])**2 + (p[2]-m[0][2])**2)
    d[1]=sqrt((p[0]-m[1][0])**2 + (p[1]-m[1][1])**2 + (p[2]-m[1][2])**2)
    d[2]=sqrt((p[0]-m[2][0])**2 + (p[1]-m[2][1])**2 + (p[2]-m[2][2])**2)
    alloc[i]=d.index(min(d))
  for i in range(k):
    alloc_ps=[p for j, p in enumerate(ps) if alloc[j] == i]
    new_mean=(sum([a[0] for a in alloc_ps]) / len(alloc_ps), sum([a[1] for a in alloc_ps]) / len(alloc_ps), sum([a[2] for a in alloc_ps]) / len(alloc_ps))
    m[i]=new_mean
  n=n+1

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
