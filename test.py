import pandas as pd
import numpy as np

x = np.array([0.0, 1.0, 2.0, 3.0,  4.0,  5.0])
y = np.array([0.0, 0.8, 0.9, 0.1, -0.8, -1.0])
list = np.array([[1,1],[2,2],[3,3]])
#list = np.append(x,y)
#y = np.array([1,1,2,2,3,3,4,4,5,5,6,6])
#y = np.array(range(12))
z = np.polyfit(x,y, 1)
y = np.empty(0)
for _, row in enumerate(list[-2:]):
    print(row)
    print(sum(row))
    y = np.append(y,sum(row))
print(np.std(list[-3:,1]))

import matplotlib.pyplot as plt
#print(z)
p = np.poly1d(z)
plt.plot(range(len(y)),y,'ro',x,p(x),'b-')
plt.show()
    