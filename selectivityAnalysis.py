# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 17:02:58 2023

@author: Catherine Wang
"""
import sys
sys.path.append("C:\scripts\Imaging analysis")
import numpy as np
import scipy.io as scio
import matplotlib.pyplot as plt
import session
from matplotlib.pyplot import figure

# from neuralFuncs import plot_average_PSTH
path = r'F:\data\BAYLORCW021\python\2023_01_25'
i = 6
layer = scio.loadmat(r'{}\layer_{}.mat'.format(path, i))
behavior = scio.loadmat(r'{}\behavior.mat'.format(path))
l1 = session.Session(layer, i, behavior)
# l1.crop_trials(245, end = 330)

# l2 = session.Session(layer_2, 2, behavior)
# l1.crop_trials(250)

# View neuron single trial psth

# for j in range(l1.num_trials):
#     l1.plot_single_trial_PSTH(j, 8)

# View the neurons
# for i in range(l1.num_neurons):
#     l1.plot_PSTH(i)

# for i in range(l2.num_neurons):
#     l2.plot_PSTH(i)
    
# Get contra and ipsi neurons

# contra, ipsi, _, _ = l1.contra_ipsi_pop()

# # Plot contra neurons
# for i in contra:
#     l1.plot_PSTH(i)

# # Plot ipsi neurons
# for i in ipsi:
#     l1.plot_PSTH(i)
    
# Get population average plots
# l1.plot_contra_ipsi_pop()

# Plot rasters for delay selective neurons:

for n in l1.get_delay_selective():
    # if l1.filter_by_deltas(n):

        # t = l1.plot_left_right_raster(n)
        # l1.plot_PSTH(n)
        # figure(figsize=(10, 10))

        # plt.show()
    # l1.plot_selectivity(n)
    l1.plot_raster_and_PSTH(n)
    l1.plot_raster_and_PSTH(n, opto=True)

    
    
    
    
    
    