from scipy.special import comb
from math import ceil
import numpy as np

def combNk(N,k):
    r = ceil(N/2.)
    sum = 0
    for b in range(ceil(k/2.),k+1):
        sum += comb(r,b) * comb(b,k-b)
    return sum

def combN(N):
    kVal = -1
    kMax = 0
    for k in range(0,N+1):
        val = combNk(N,k)
        if val > kMax:
            kVal = k
            kMax = val
    return [kVal, kMax]

import matplotlib.pyplot as plt
num = []
val = []
kVals = []
for n in range(20, 60+1):
    num.append(n)
    combN_val = combN(n)
    val.append(combN_val[1])
    kVals.append(combN_val[0])

for n in range(0,41):
    print(val[n])
    print(kVals[n])
    print(num[n])

plt.scatter(num, val)
plt.xlabel('Number of containers N')
plt.ylabel('Maximal number of states')
plt.xticks(range(20,61,10))
plt.show()

print(combN(20))
print(combN(30))
print(combN(60))

import matplotlib.pyplot as plt
num = []
val = []
kVals = []
for n in range(20, 60+1):
    num.append(ceil(n/2.))
    combN_val = combN(n)
    val.append(combN_val[1])
    kVals.append(combN_val[0])

plt.scatter(num, val)
plt.xlabel('Length of train r')
plt.ylabel('Maximal number of states')
plt.xticks(range(10,31,5))
plt.show()