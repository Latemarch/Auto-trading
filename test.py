'''
import pandas as pd
import numpy as np

x = np.array([0.0, 1.0, 2.0, 3.0,  4.0,  5.0])
y = np.array([0.0, 0.8, 0.9, 0.1, -0.8, -1.0])
z = np.polyfit(x, y, 1)

import matplotlib.pyplot as plt
print(z)
p = np.poly1d(z)
plt.plot(range(len(y)),y,'ro',x,p(x),'b-')
plt.show()
'''
def add(a:list):
    a['1'].append(1)

a = {'1':[],'2':[]}
add(a)
print(a)
print(a['1'])
    