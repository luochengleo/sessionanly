__author__ = 'luocheng'

from scipy.stats.stats import pearsonr
from scipy.stats.stats import kendalltau
x=  [1,2,3,4,5,6]
y = [0,1,2,4,5,6]

print pearsonr(x,y)
print kendalltau(x,y)