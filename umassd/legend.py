# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 11:58:50 2017

@author: Shekar
"""

import pylab

fig =  pylab.figure()
legend = pylab.figure(figsize=(3,2))
ax = fig.add_subplot(111)
lines = ax.plot(range(10), pylab.randn(10), range(10), pylab.randn(10))
legend.legend(lines, ('one', 'two'), 'center')
fig.show()
legend.show()
#legend.savefig('legend.png')