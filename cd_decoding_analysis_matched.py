# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 12:59:23 2023

@author: Catherine Wang
"""


import sys
sys.path.append("C:\scripts\Imaging analysis")
import numpy as np
import scipy.io as scio
import matplotlib.pyplot as plt
import session
from matplotlib.pyplot import figure
import decon
from scipy.stats import chisquare
import pandas as pd
from activityMode import Mode

# Plot choice decoding in control vs opto trials


#%%
paths = [[r'F:\data\BAYLORCW032\python\2023_10_08',
          r'F:\data\BAYLORCW032\python\2023_10_16',
          r'F:\data\BAYLORCW032\python\2023_10_25',
          r'F:\data\BAYLORCW032\python\cellreg\layer{}\1008_1016_1025pairs_proc.npy'],
         
         [ r'F:\data\BAYLORCW034\python\2023_10_12',
            r'F:\data\BAYLORCW034\python\2023_10_22',
            r'F:\data\BAYLORCW034\python\2023_10_27',
            r'F:\data\BAYLORCW034\python\cellreg\layer{}\1012_1022_1027pairs_proc.npy'],
         
         [r'F:\data\BAYLORCW036\python\2023_10_09',
            r'F:\data\BAYLORCW036\python\2023_10_19',
            r'F:\data\BAYLORCW036\python\2023_10_30',
            r'F:\data\BAYLORCW036\python\cellreg\layer{}\1009_1019_1030pairs_proc.npy'],
        ]

#%% Matched
#%% CW32 matched

# CONTRA
paths = [r'F:\data\BAYLORCW032\python\2023_10_05',
          r'F:\data\BAYLORCW032\python\2023_10_19',
          r'F:\data\BAYLORCW032\python\2023_10_24',]
for path in paths:
    
    l1 = Mode(path, use_reg=True, triple=True)
    

    orthonormal_basis, mean, db, acc_within = l1.decision_boundary()
    print(np.mean(acc_within))
    
    
    
    plt.bar([0], [np.mean(acc_within)])
    plt.scatter(np.zeros(len(acc_within)), np.mean(acc_within,axis=1), color = 'r')
    # plt.errorbar([0], [np.mean(acc_within)],
    #              [np.std(acc_within)/np.sqrt(len(acc_within))],
    #              color = 'r')
    plt.xticks([0], ['Left ALM -> behavior'])
    plt.ylim(bottom=0.4, top =1)
    plt.show()
