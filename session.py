# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 10:46:39 2023

@author: Catherine Wang
"""
# from neuralFuncs import plot_PSTH
import numpy as np
from numpy import concatenate as cat
import matplotlib.pyplot as plt
from scipy import stats
import copy
import scipy.io as scio
from sklearn.preprocessing import normalize
from matplotlib.pyplot import figure
from matplotlib.colors import ListedColormap
from sklearn.preprocessing import normalize
import os

class Session:
    
    def __init__(self, path, layer_num='all', guang=False, passive=False):
        
        if layer_num != 'all':
            
            layer_og = scio.loadmat(r'{}\layer_{}.mat'.format(path, layer_num))
            layer = copy.deepcopy(layer_og)
            self.dff = layer['dff']

        else:
            # Load all layers
            self.dff = None
            for layer in os.listdir(path):
                if 'layer' in layer:
                    layer_og = scio.loadmat(r'{}\{}'.format(path, layer))
                    layer = copy.deepcopy(layer_og)
                    
                    if self.dff == None:
                        
                        
                        self.dff = layer['dff']
                        self.num_trials = layer['dff'].shape[1] 
                    else:

                        for t in range(self.num_trials):
                            add = layer['dff'][0, t]
                            self.dff[0, t] = np.vstack((self.dff[0, t], add))
                        
        
        behavior = scio.loadmat(r'{}\behavior.mat'.format(path))
        self.path = path
        self.layer_num = layer_num
        self.passive = passive
        self.num_neurons = self.dff[0,0].shape[0]

        self.num_trials = self.dff.shape[1] 
        
        self.time_cutoff = self.determine_cutoff()
        
        self.recording_loc = 'l'
        self.skew = layer['skew']
        
        self.good_neurons = np.where(self.skew>=1)[1]
        
        if passive:
            self.i_good_trials = range(4, self.num_trials)
        else:
            self.i_good_trials = cat(behavior['i_good_trials']) - 1 # zero indexing in python
        
        self.L_correct = cat(behavior['L_hit_tmp'])
        self.R_correct = cat(behavior['R_hit_tmp'])
        
        self.early_lick = cat(behavior['LickEarly_tmp'])
        
        self.L_wrong = cat(behavior['L_miss_tmp'])
        self.R_wrong = cat(behavior['R_miss_tmp'])
        
        self.L_ignore = cat(behavior['L_ignore_tmp'])
        self.R_ignore = cat(behavior['R_ignore_tmp'])
        
        self.stim_ON = cat(behavior['StimDur_tmp']) > 0
        if 'StimLevel' in behavior.keys():
            self.stim_level = cat(behavior['StimLevel'])
            
        if self.i_good_trials[-1] > self.num_trials:
            
            print('More Bpod trials than 2 photon trials')
            self.i_good_trials = [i for i in self.i_good_trials if i < self.num_trials]
            self.stim_ON = self.stim_ON[:self.num_trials]
        
        
        # Measure that automatically crops out water leak trials before norming
        if not self.find_low_mean_F():

            self.plot_mean_F()

            if guang:
                # Guang's data
                self.num_neurons = layer['dff'][0,0].shape[1]  # Guang's data
    
                for t in range(self.num_trials):
                    self.dff[0, t] = self.dff[0, t].T
            else:
                # self.normalize_all_by_neural_baseline()
                self.normalize_all_by_baseline()
                # self.normalize_by_histogram()
                # self.normalize_all_by_histogram()
                self.normalize_z_score()    
        
    def determine_cutoff(self):
        
        cutoff = 1e10
        
        for t in range(self.num_trials):
            
            if self.dff[0, t].shape[1] < cutoff:
                
                cutoff = self.dff[0, t].shape[1]
        
        print("Minimum cutoff is {}".format(cutoff))
        
        return cutoff
    
    def find_low_mean_F(self, cutoff = 100):
        
        # Usual cutoff is 50
        # Reject outliers based on medians
        meanf = np.array([])
        for trial in range(self.num_trials):
            meanf = np.append(meanf, np.mean(cat(self.dff[0, trial])))
        
        med = np.median(meanf) # median approach
        
        trial_idx = np.where(meanf < cutoff)[0]
        
        if trial_idx.size == 0:
            
            return 0
        
        else:
            print('Water leak trials: {}'.format(trial_idx))

            self.crop_trials(0, singles=True, arr = trial_idx)
            return 1
        
    def reject_outliers(data, m = 2.):
        
        d = np.abs(data - np.median(data))
        mdev = np.median(d)
        s = d/mdev if mdev else np.zero(len(d))
        
        return data[s<m]
    
    def plot_mean_F(self):
        
        # Plots mean F for all neurons over trials in session
        meanf = list()
        for trial in range(self.num_trials):
            meanf.append(np.mean(cat(self.dff[0, trial])))
        
        plt.plot(range(self.num_trials), meanf, 'b-')
        plt.title("Mean F for layer {}".format(self.layer_num))
        plt.show()

    def crop_trials(self, trial_num, end=False, singles = False, arr = []):
        
        # If called, crops out all trials after given trial number
        # Can optionally crop from trial_num to end indices
        
        if not end and not singles:
            
            self.L_correct = self.L_correct[:trial_num]
            self.R_correct = self.R_correct[:trial_num]
            
            self.dff = self.dff[:, :trial_num]
            
            self.i_good_trials = [i for i in self.i_good_trials if i < trial_num]
            self.num_trials = trial_num
            self.stim_ON = self.stim_ON[:trial_num]
            if self.passive:
                self.stim_level = self.stim_level[:trial_num]
            # self.normalize_all_by_baseline()
            # self.normalize_z_score()    

            
            # self.plot_mean_F()
            
        
        elif singles:
            
            self.L_correct = np.delete(self.L_correct, arr)
            self.R_correct = np.delete(self.R_correct, arr)
            
            self.dff = np.delete(self.dff, arr)
            self.dff = np.reshape(self.dff, (1,-1))
            
            igoodremove = np.where(np.in1d(self.i_good_trials, arr))[0]
            self.i_good_trials = np.delete(self.i_good_trials, igoodremove)
            self.num_trials = self.num_trials - len(arr)            
            self.stim_ON = np.delete(self.stim_ON, arr)
            if self.passive:
                self.stim_level = np.delete(self.stim_level, arr)
            # self.normalize_all_by_baseline()
            # self.normalize_z_score()   

            # self.plot_mean_F()
            
        else:
            
            arr = np.arange(trial_num, end)

            self.L_correct = np.delete(self.L_correct, arr)
            self.R_correct = np.delete(self.R_correct, arr)
            
            self.dff = np.delete(self.dff, arr)
            self.dff = np.reshape(self.dff, (1,-1))
            
            igoodremove = np.where(np.in1d(self.i_good_trials, arr))[0]
            self.i_good_trials = np.delete(self.i_good_trials, igoodremove)
            self.num_trials = self.num_trials - len(arr)            
            self.stim_ON = np.delete(self.stim_ON, arr)
            if self.passive:
                self.stim_level = np.delete(self.stim_level, arr)

            # self.i_good_trials = [i for i in self.i_good_trials if i < trial_num or i > end]
            # self.num_trials = trial_num            
            # self.stim_ON = np.append(self.stim_ON[:trial_num], self.stim_ON[end:])

            # self.normalize_all_by_baseline()
            # self.normalize_z_score()   

            # self.plot_mean_F()

        self.plot_mean_F()

        self.normalize_all_by_baseline()
        self.normalize_z_score()    
        
        
        print('New number of good trials: {}'.format(len(self.i_good_trials)))
    
    def lick_correct_direction(self, direction):
        ## Returns list of indices of lick left correct trials
        
        if direction == 'l':
            idx = np.where(self.L_correct == 1)[0]
        elif direction == 'r':
            idx = np.where(self.R_correct == 1)[0]
        else:
            raise Exception("Sorry, only 'r' or 'l' input accepted!")
            
        early_idx = np.where(self.early_lick == 1)[0]
        
        idx = [i for i in idx if i not in early_idx]
        
        idx = [i for i in idx if i in self.i_good_trials]
        
        return idx
    
    def lick_incorrect_direction(self, direction):
        ## Returns list of indices of lick left correct trials
        
        if direction == 'l':
            idx = np.where(self.L_wrong == 1)[0]
        elif direction == 'r':
            idx = np.where(self.R_wrong == 1)[0]
        else:
            raise Exception("Sorry, only 'r' or 'l' input accepted!")
            
        early_idx = np.where(self.early_lick == 1)[0]
        
        idx = [i for i in idx if i not in early_idx]
        
        idx = [i for i in idx if i in self.i_good_trials]
        
        return idx
    
    def get_trace_matrix(self, neuron_num):
        
        ## Returns matrix of all trial firing rates of a single neuron for lick left
        ## and lick right trials. Firing rates are normalized with individual trial
        ## baselines as well as overall firing rate z-score normalized.
        
        right_trials = self.lick_correct_direction('r')
        left_trials = self.lick_correct_direction('l')
        
        # Filter out opto trials
        right_trials = [r for r in right_trials if not self.stim_ON[r]]
        left_trials = [r for r in left_trials if not self.stim_ON[r]]
        
        R_av_dff = []
        for i in right_trials:
            # R_av_dff += [self.normalize_by_baseline(self.dff[0, i][neuron_num, :self.time_cutoff])]
            R_av_dff += [self.dff[0, i][neuron_num, :self.time_cutoff]]

        L_av_dff = []
        for i in left_trials:
            # L_av_dff += [self.normalize_by_baseline(self.dff[0, i][neuron_num, :self.time_cutoff])]
            L_av_dff += [self.dff[0, i][neuron_num, :self.time_cutoff]]
            
            
        return R_av_dff, L_av_dff
    
    def get_opto_trace_matrix(self, neuron_num, error=False):
        
        
        right_trials = self.lick_correct_direction('r')
        left_trials = self.lick_correct_direction('l')
        
        if error:
            right_trials = self.lick_incorrect_direction('r')
            left_trials = self.lick_incorrect_direction('l')
        
        # Filter for opto trials
        right_trials = [r for r in right_trials if self.stim_ON[r]]
        left_trials = [r for r in left_trials if self.stim_ON[r]]

        
        R_av_dff = []
        for i in right_trials:
            
            R_av_dff += [self.dff[0, i][neuron_num, :self.time_cutoff]]
        
        L_av_dff = []
        for i in left_trials:

            L_av_dff += [self.dff[0, i][neuron_num, :self.time_cutoff]]
            
        
            
        return R_av_dff, L_av_dff
    
    def get_trace_matrix_multiple(self, neuron_nums, opto=False, error=False, both=False):
        
        ## Returns matrix of average firing rates of a list of neurons for lick left
        ## and lick right trials. Firing rates are normalized with individual trial
        ## baselines as well as overall firing rate z-score normalized.
        
        R, L = [], []
        
        for neuron_num in neuron_nums:
            if both:
                right_trials = cat((self.lick_correct_direction('r'), self.lick_incorrect_direction('r')))
                left_trials = cat((self.lick_correct_direction('l'), self.lick_incorrect_direction('l')))
            
            elif not error:
                right_trials = self.lick_correct_direction('r')
                left_trials = self.lick_correct_direction('l')
            elif error:
                right_trials = self.lick_incorrect_direction('r')
                left_trials = self.lick_incorrect_direction('l')
                
            # Filter out opto trials
            if not opto:
                right_trials = [r for r in right_trials if not self.stim_ON[r]]
                left_trials = [r for r in left_trials if not self.stim_ON[r]]
            elif opto:
                right_trials = [r for r in right_trials if self.stim_ON[r]]
                left_trials = [r for r in left_trials if self.stim_ON[r]]           
                
            
            R_av_dff = []
            for i in right_trials:
                # R_av_dff += [self.normalize_by_baseline(self.dff[0, i][neuron_num, :self.time_cutoff])]
                R_av_dff += [self.dff[0, i][neuron_num, :self.time_cutoff]]
    
            L_av_dff = []
            for i in left_trials:
                # L_av_dff += [self.normalize_by_baseline(self.dff[0, i][neuron_num, :self.time_cutoff])]
                L_av_dff += [self.dff[0, i][neuron_num, :self.time_cutoff]]
            
            R += [np.mean(R_av_dff, axis = 0)]
            L += [np.mean(L_av_dff, axis = 0)]
            
        return np.array(R), np.array(L)

    def plot_PSTH(self, neuron_num, opto = False):
        
        ## Plots single neuron PSTH for R/L trials
        
        if not opto:
            R, L = self.get_trace_matrix(neuron_num)
        else:
            R, L = self.get_opto_trace_matrix(neuron_num)

        
        R_av, L_av = np.mean(R, axis = 0), np.mean(L, axis = 0)
        
        left_err = np.std(L, axis=0) / np.sqrt(len(L)) 
        right_err = np.std(R, axis=0) / np.sqrt(len(R))
                    
        plt.plot(L_av, 'r-')
        plt.plot(R_av, 'b-')
        
        x = range(self.time_cutoff)

        plt.fill_between(x, L_av - left_err, 
                 L_av + left_err,
                 color=['#ffaeb1'])
        plt.fill_between(x, R_av - right_err, 
                 R_av + right_err,
                 color=['#b4b2dc'])
        plt.title("Neuron {}: R/L PSTH".format(neuron_num))
        plt.show()

    def plot_single_trial_PSTH(self, trial, neuron_num):
        
        plt.plot(self.dff[0, trial][neuron_num], 'b-')
        plt.title("Neuron {}: PSTH for trial {}".format(neuron_num, trial))
        plt.show()

    def plot_population_PSTH(self, neurons, opto = False):
        
        # Returns the population average activity for L/R trials of these neurons
        
        overall_R = []
        overall_L = []

        for neuron_num in neurons:
            
            if not opto:
                R, L = self.get_trace_matrix(neuron_num)
            else:
                R, L = self.get_opto_trace_matrix(neuron_num)
                
            overall_R += R
            overall_L += L
        
        R_av, L_av = np.mean(overall_R, axis = 0), np.mean(overall_L, axis = 0)
        
        left_err = np.std(overall_L, axis=0) / np.sqrt(len(overall_L)) 
        right_err = np.std(overall_R, axis=0) / np.sqrt(len(overall_R))
                    
        plt.plot(L_av, 'r-')
        plt.plot(R_av, 'b-')
        
        x = range(self.time_cutoff)

        plt.fill_between(x, L_av - left_err, 
                 L_av + left_err,
                 color=['#ffaeb1'])
        plt.fill_between(x, R_av - right_err, 
                 R_av + right_err,
                 color=['#b4b2dc'])
        plt.title("Neural population PSTH")
        plt.show()

    def normalize_by_baseline(self, trace):
        
        # Function to normalize by first 7 time points
        
        # return trace
        
        mean = np.mean(trace[:7])
        if mean == 0:
            raise Exception("Neuron has mean 0.")
            
        return (trace - mean) / mean # norm by F0
    
    def normalize_all_by_neural_baseline(self):
        
        # Normalize all neurons by neural trial-averaged F0
        
        # for i in range(self.num_neurons):
        for i in self.good_neurons:

            nmean = np.mean([self.dff[0, t][i, :7] for t in range(self.num_trials)]).copy()
            
            for j in range(self.num_trials):
                
                # nmean = np.mean(self.dff[0, j][i, :7])
                self.dff[0, j][i] = (self.dff[0, j][i] - nmean) / nmean
        
        return None
    
    def normalize_all_by_baseline(self):
        
        # Normalize all neurons by individual trial-averaged F0
        
        for i in range(self.num_neurons):
        # for i in self.good_neurons:
            
            # nmean = np.mean([self.dff[0, t][i, :7] for t in range(self.num_trials)]).copy()
            
            for j in range(self.num_trials):
                
                nmean = np.mean(self.dff[0, j][i, 3:7]) # later cutoff because of transient activation
                self.dff[0, j][i] = (self.dff[0, j][i] - nmean) / nmean
        
        return None

    def normalize_by_histogram(self):
        
        # Normalize all neurons by individual trial-averaged F0
        
        for i in range(self.num_neurons):
        # for i in self.good_neurons:
            
            nmean = np.quantile(cat([self.dff[0,t][i, :] for t in range(self.num_trials)]), q=0.10)
            
            for j in range(self.num_trials):
                
                self.dff[0, j][i] = (self.dff[0, j][i] - nmean) / nmean
        
        return None
    
    def normalize_all_by_histogram(self):
        
        # Normalize all neurons by individual trial-averaged F0
        
        for i in range(self.num_neurons):
                        
            for j in range(self.num_trials):
               
                nmean = np.quantile(self.dff[0, j][i, :], q=0.10)

                self.dff[0, j][i] = (self.dff[0, j][i] - nmean) / nmean
        
        return None
    
    def normalize_z_score(self):
        
        # Normalize by mean of all neurons in layer
        
        overall_mean = np.mean(cat([cat(i) for i in self.dff[0]])).copy()
        std = np.std(cat([cat(i) for i in self.dff[0]])).copy()
        
        for i in range(self.num_trials):
            for j in range(self.num_neurons):
                self.dff[0, i][j] = (self.dff[0, i][j] - overall_mean) / std
                
        # self.dff = normalize(self.dff)
        
        return None

    def get_epoch_selective(self, epoch, p = 0.01):
        selective_neurons = []
        for neuron in range(self.num_neurons):
        # for neuron in self.good_neurons:
            right, left = self.get_trace_matrix(neuron)
            left_ = [l[epoch] for l in left]
            right_ = [r[epoch] for r in right]
            tstat, p_val = stats.ttest_ind(np.mean(left_, axis = 1), np.mean(right_, axis = 1))
            # p = 0.01/self.num_neurons
            # p = 0.01
            # p = 0.0001
            if p_val < p:
                selective_neurons += [neuron]
        # print("Total delay selective neurons: ", len(selective_neurons))
        self.selective_neurons = selective_neurons
        return selective_neurons
   
    
    def screen_preference(self, neuron_num, epoch, samplesize = 10):

        # Input: neuron of interest
        # Output: (+) if left pref, (-) if right pref, then indices of trials to plot
        
        # All trials where the mouse licked left or right AND non stim
        
        R, L = self.get_trace_matrix(neuron_num)
        l_trials = range(len(L))  
        r_trials = range(len(R))
        
        # Skip neuron if less than 15
        if len(l_trials) < 15 or len(r_trials) < 15:
            raise Exception("Neuron {} has fewer than 15 trials in R or L lick trials".format(neuron_num))
            return 0
        
        # Pick 20 random trials as screen for left and right
        screen_l = np.random.choice(l_trials, size = samplesize, replace = False)
        screen_r = np.random.choice(r_trials, size = samplesize, replace = False)
    
        # Remainder of trials are left for plotting in left and right separately
        test_l = [t for t in l_trials if t not in screen_l]
        test_r = [t for t in r_trials if t not in screen_r]
        
        # Compare late delay epoch for preference
        avg_l = np.mean([np.mean(L[i][epoch]) for i in screen_l])
        avg_r = np.mean([np.mean(R[i][epoch]) for i in screen_r])
    
        return avg_l > avg_r, test_l, test_r

    def plot_selectivity(self, neuron_num, plot=True, epoch=range(21,28)):
        
        R, L = self.get_trace_matrix(neuron_num)
        pref, l, r = self.screen_preference(neuron_num, epoch)
        left_trace = [L[i] for i in l]
        right_trace = [R[i] for i in r]

        if pref: # prefers left
            sel = np.mean(left_trace, axis = 0) - np.mean(right_trace, axis=0)
        else:
            sel = np.mean(right_trace, axis = 0) - np.mean(left_trace, axis=0)
        
        if plot:
            direction = 'Left' if pref else 'Right'
            plt.plot(range(self.time_cutoff), sel, 'b-')
            plt.axhline(y=0)
            plt.title('Selectivity of neuron {}: {} selective'.format(neuron_num, direction))
            plt.show()
        
        return sel
    
    def contra_ipsi_pop(self, epoch):
        
        # Returns the neuron ids for contra and ipsi populations

        selective_neurons = self.get_epoch_selective(epoch)
        
        contra_neurons = []
        ipsi_neurons = []
        
        contra_LR, ipsi_LR = dict(), dict()
        contra_LR['l'], contra_LR['r'] = [], []
        ipsi_LR['l'], ipsi_LR['r'] = [], []
        
        
        for neuron_num in selective_neurons:
            
            # Skip sessions with fewer than 15 neurons
            if self.screen_preference(neuron_num, epoch) != 0:
                
                R, L = self.get_trace_matrix(neuron_num)

                pref, test_l, test_r = self.screen_preference(neuron_num, epoch) 
        
                if self.recording_loc == 'l':

                    if pref:
                        # print("Ipsi_preferring: {}".format(neuron_num))
                        ipsi_neurons += [neuron_num]
                        ipsi_LR['l'] += [L[i] for i in test_l]
                        ipsi_LR['r'] += [R[i] for i in test_r]
                    else:
                        # print("Contra preferring: {}".format(neuron_num))
                        contra_neurons += [neuron_num] 
                        contra_LR['l'] += [L[i] for i in test_l]
                        contra_LR['r'] += [R[i] for i in test_r]
                    
                elif self.recording_loc == 'r':

                    if not pref:
                        ipsi_neurons += [neuron_num]
                        ipsi_LR['l'] += [L[i] for i in test_l]
                        ipsi_LR['r'] += [R[i] for i in test_r]
                    else:
                        contra_neurons += [neuron_num] 
                        contra_LR['l'] += [L[i] for i in test_l]
                        contra_LR['r'] += [R[i] for i in test_r]
                        
        return contra_neurons, ipsi_neurons, contra_LR, ipsi_LR
    
    def plot_contra_ipsi_pop(self, epoch=range(21,28)):
        
        contra_neurons, ipsi_neurons, contra_trace, ipsi_trace = self.contra_ipsi_pop(epoch)
        
        if len(ipsi_neurons) != 0:
        
            overall_R, overall_L = ipsi_trace['r'], ipsi_trace['l']
            
            R_av, L_av = np.mean(overall_R, axis = 0), np.mean(overall_L, axis = 0)
            
            left_err = np.std(overall_L, axis=0) / np.sqrt(len(overall_L)) 
            right_err = np.std(overall_R, axis=0) / np.sqrt(len(overall_R))
                        
            plt.plot(L_av, 'r-')
            plt.plot(R_av, 'b-')
            
            x = range(self.time_cutoff)
    
            plt.fill_between(x, L_av - left_err, 
                     L_av + left_err,
                     color=['#ffaeb1'])
            plt.fill_between(x, R_av - right_err, 
                     R_av + right_err,
                     color=['#b4b2dc'])
            plt.title("Ipsi-preferring neurons")
            plt.show()
        
        else:
            print('No ipsi selective neurons')
    
        if len(contra_neurons) != 0:

            overall_R, overall_L = contra_trace['r'], contra_trace['l']
            
            R_av, L_av = np.mean(overall_R, axis = 0), np.mean(overall_L, axis = 0)
            
            left_err = np.std(overall_L, axis=0) / np.sqrt(len(overall_L)) 
            right_err = np.std(overall_R, axis=0) / np.sqrt(len(overall_R))
                        
            plt.plot(L_av, 'r-')
            plt.plot(R_av, 'b-')
            
            x = range(self.time_cutoff)
    
            plt.fill_between(x, L_av - left_err, 
                      L_av + left_err,
                      color=['#ffaeb1'])
            plt.fill_between(x, R_av - right_err, 
                      R_av + right_err,
                      color=['#b4b2dc'])
            plt.title("Contra-preferring neurons")
            plt.show()
        else:
            print('No contra selective neurons')
            
            
    def plot_individual_raster(self, neuron_num):
        
                
        trace = [self.dff[0, t][neuron_num, :self.time_cutoff] for t in range(self.num_trials)]

        vmin, vmax = min(cat(trace)), max(cat(trace))
        trace = np.matrix(trace)
        
        plt.matshow(trace, cmap='gray', vmin=vmin, vmax=vmax)
        plt.axis('off')
        
        return trace
        
    def plot_left_right_raster(self, neuron_num, opto=False):
        
        r, l = self.get_trace_matrix(neuron_num)
        if opto:
            r, l = self.get_opto_trace_matrix(neuron_num)

        vmin, vmax = min(cat(cat((r,l)))), max(cat(cat((r,l))))
        
        r_trace, l_trace = np.matrix(r), np.matrix(l)
        
        stack = np.vstack((r_trace, l_trace))
        
        plt.matshow(stack, cmap='gray') #, norm ="log") #, vmin=vmin, vmax=vmax)
        plt.axis('off')
        # plt.figsize(10,01)
        return stack
        
    def plot_selective_raster(self, neuron_num):
        
        return None
    
    def filter_by_deltas(self, neuron_num):
        
        # Filters out neurons without significant changes in trials
        
        r, l = self.get_trace_matrix(neuron_num)
        
        all_t = cat((r, l))
        ds = []
        for t in all_t:
            ds += [max(t) - min(t)]
            
        if np.median(ds) > 500:
            return True
        else:
            return False
        
    def plot_raster_and_PSTH(self, neuron_num, opto=False):

        if not opto:
            R, L = self.get_trace_matrix(neuron_num)
            r, l = self.get_trace_matrix(neuron_num)
            title = "Neuron {}: Raster and PSTH".format(neuron_num)

        else:
            R, L = self.get_opto_trace_matrix(neuron_num)
            r, l = self.get_opto_trace_matrix(neuron_num)
            title = "Neuron {}: Opto Raster and PSTH".format(neuron_num)
        
        r_trace, l_trace = np.matrix(r), np.matrix(l)
        
        # r_trace, l_trace = r_trace[:, 3:], l_trace[:, 3:]
        
        # stack = np.vstack((r_trace, np.ones(self.time_cutoff), l_trace))
        stack = np.vstack((r_trace, l_trace))


        
        R_av, L_av = np.mean(R, axis = 0), np.mean(L, axis = 0)
        
        left_err = np.std(L, axis=0) / np.sqrt(len(L)) 
        right_err = np.std(R, axis=0) / np.sqrt(len(R))
        
        # R_av, L_av, left_err, right_err = R_av[3:], L_av[3:], left_err[3:], right_err[3:]
                    

        f, axarr = plt.subplots(2, sharex=True)

        axarr[0].matshow(stack, cmap='gray', interpolation='nearest', aspect='auto')
        axarr[0].axis('off')
        
        axarr[1].plot(L_av, 'r-')
        axarr[1].plot(R_av, 'b-')
        
        x = range(self.time_cutoff)
        # x = x[3:]
        
        axarr[1].fill_between(x, L_av - left_err, 
                 L_av + left_err,
                 color=['#ffaeb1'])
        axarr[1].fill_between(x, R_av - right_err, 
                 R_av + right_err,
                 color=['#b4b2dc'])
        
        axarr[0].set_title(title)
        plt.show()
        

    def plot_rasterPSTH_sidebyside(self, neuron_num):
        
        R, L = self.get_trace_matrix(neuron_num)
        r, l = self.get_trace_matrix(neuron_num)
        title = "Neuron {}: Control".format(neuron_num)


        # f, axarr = plt.subplots(2,2, sharex='col', sharey = 'row')
        f, axarr = plt.subplots(2,2, sharex='col')
        
        r_trace, l_trace = np.matrix(r), np.matrix(l)
        
        stack = np.vstack((r_trace, np.ones(self.time_cutoff), l_trace))
        stack = np.vstack((r_trace, l_trace))


        
        R_av, L_av = np.mean(R, axis = 0), np.mean(L, axis = 0)
        
        left_err = np.std(L, axis=0) / np.sqrt(len(L)) 
        right_err = np.std(R, axis=0) / np.sqrt(len(R))
                    

        axarr[0, 0].matshow(stack, cmap='gray', interpolation='nearest', aspect='auto')
        axarr[0, 0].axis('off')
        
        axarr[1, 0].plot(L_av, 'r-')
        axarr[1, 0].plot(R_av, 'b-')
        axarr[1, 0].axvline(7, linestyle = '--')
        axarr[1, 0].axvline(13, linestyle = '--')
        axarr[1, 0].axvline(28, linestyle = '--')
        
        x = range(self.time_cutoff)

        axarr[1, 0].fill_between(x, L_av - left_err, 
                 L_av + left_err,
                 color=['#ffaeb1'])
        axarr[1, 0].fill_between(x, R_av - right_err, 
                 R_av + right_err,
                 color=['#b4b2dc'])
        
        axarr[0,0].set_title(title)
        
    
        R, L = self.get_opto_trace_matrix(neuron_num)
        r, l = self.get_opto_trace_matrix(neuron_num)
        title = "Neuron {}: Opto".format(neuron_num)

                
        r_trace, l_trace = np.matrix(r), np.matrix(l)
        
        stack = np.vstack((r_trace, np.ones(self.time_cutoff), l_trace))
        stack = np.vstack((r_trace, l_trace))

        R_av, L_av = np.mean(R, axis = 0), np.mean(L, axis = 0)
        vmax = max(cat([R_av, L_av]))

        left_err = np.std(L, axis=0) / np.sqrt(len(L)) 
        right_err = np.std(R, axis=0) / np.sqrt(len(R))
                    

        axarr[0, 1].matshow(stack, cmap='gray', interpolation='nearest', aspect='auto')
        axarr[0, 1].axis('off')
        
        axarr[1, 1].plot(L_av, 'r-')
        axarr[1, 1].plot(R_av, 'b-')
        axarr[1, 1].axvline(7, linestyle = '--')
        axarr[1, 1].axvline(13, linestyle = '--')
        axarr[1, 1].axvline(28, linestyle = '--')
        axarr[1, 1].hlines(y=vmax, xmin=13, xmax=18, linewidth=10, color='lightblue')
        
        x = range(self.time_cutoff)

        axarr[1, 1].fill_between(x, L_av - left_err, 
                 L_av + left_err,
                 color=['#ffaeb1'])
        axarr[1, 1].fill_between(x, R_av - right_err, 
                 R_av + right_err,
                 color=['#b4b2dc'])
        
        axarr[0,1].set_title(title)
        
        plt.show()

### EPHYS PLOTS TO MY DATA ###

    def plot_number_of_sig_neurons(self, save=False):
        
        contra = np.zeros(self.time_cutoff)
        ipsi = np.zeros(self.time_cutoff)
        x = np.arange(-5.97,4,0.2)[:self.time_cutoff]

        for t in range(self.time_cutoff):
            
            sig_neurons = []

            for n in range(self.num_neurons):
                
                r, l = self.get_trace_matrix(n)
                r, l = np.matrix(r), np.matrix(l)
                t_val, p = stats.ttest_ind(r[:, t], l[:, t])
                
                if p < 0.01:
                     
                    if np.mean(r[:, t]) < np.mean(l[:, t]):
                        sig_neurons += [1]  # ipsi
                        
                    elif np.mean(r[:, t]) > np.mean(l[:, t]):
                        sig_neurons += [-1]  # contra
                    
                    else:
                        print("Error on neuron {} at time {}".format(n,t))

                else:
                    
                    sig_neurons += [0]
            
            contra[t] = sum(np.array(sig_neurons) == -1)
            ipsi[t] = sum(np.array(sig_neurons) == 1)

        plt.bar(x, contra, color = 'b', edgecolor = 'white', width = 0.2, label = 'contra')
        plt.bar(x, -ipsi, color = 'r',edgecolor = 'white', width = 0.2, label = 'ipsi')
        plt.axvline(-4.3)
        plt.axvline(-3)
        plt.axvline(0)
        
        plt.ylabel('Number of sig sel neurons')
        plt.xlabel('Time from Go cue (s)')
        plt.legend()
        
        if save:
            plt.savefig(self.path + r'number_sig_neurons.png')
        
        plt.show()
        
    def selectivity_table_by_epoch(self, save=False):
        
        # Plots fractions of contra/ipsi neurons and their overall trace

        f, axarr = plt.subplots(4,3, sharex='col', figsize=(14, 12))
        epochs = [range(self.time_cutoff), range(8,14), range(19,28), range(29,self.time_cutoff)]
        x = np.arange(-5.97,4,0.2)[:self.time_cutoff]
        titles = ['Whole-trial', 'Sample', 'Delay', 'Response']
        
        for i in range(4):
            
            contra_neurons, ipsi_neurons, contra_trace, ipsi_trace = self.contra_ipsi_pop(epochs[i])

            # Bar plot
            axarr[i, 0].bar(['Contra', 'Ipsi'], [len(contra_neurons)/len(self.selective_neurons),
                                    len(ipsi_neurons)/len(self.selective_neurons)], 
                            color = ['b', 'r'])
            
            axarr[i, 0].set_ylim(0,1)
            axarr[i, 0].set_title(titles[i])
            
            if len(ipsi_neurons) != 0:
            
                overall_R, overall_L = ipsi_trace['r'], ipsi_trace['l']
                
                R_av, L_av = np.mean(overall_R, axis = 0), np.mean(overall_L, axis = 0)
                
                left_err = np.std(overall_L, axis=0) / np.sqrt(len(overall_L)) 
                right_err = np.std(overall_R, axis=0) / np.sqrt(len(overall_R))
                            
                axarr[i, 2].plot(x, L_av, 'r-')
                axarr[i, 2].plot(x, R_av, 'b-')
                        
                axarr[i, 2].fill_between(x, L_av - left_err, 
                         L_av + left_err,
                         color=['#ffaeb1'])
                axarr[i, 2].fill_between(x, R_av - right_err, 
                         R_av + right_err,
                         color=['#b4b2dc'])
                axarr[i, 2].set_title("Ipsi-preferring neurons")
            
            else:
                print('No ipsi selective neurons')
        
            if len(contra_neurons) != 0:
    
                overall_R, overall_L = contra_trace['r'], contra_trace['l']
                
                R_av, L_av = np.mean(overall_R, axis = 0), np.mean(overall_L, axis = 0)
                
                left_err = np.std(overall_L, axis=0) / np.sqrt(len(overall_L)) 
                right_err = np.std(overall_R, axis=0) / np.sqrt(len(overall_R))
                            
                axarr[i, 1].plot(x, L_av, 'r-')
                axarr[i, 1].plot(x, R_av, 'b-')
                        
                axarr[i, 1].fill_between(x, L_av - left_err, 
                          L_av + left_err,
                          color=['#ffaeb1'])
                axarr[i, 1].fill_between(x, R_av - right_err, 
                          R_av + right_err,
                          color=['#b4b2dc'])
                axarr[i, 1].set_title("Contra-preferring neurons")

            else:
                print('No contra selective neurons')
                
        axarr[0,0].set_ylabel('Proportion of neurons')
        axarr[0,1].set_ylabel('dF/F0')
        axarr[3,1].set_xlabel('Time from Go cue (s)')
        axarr[3,2].set_xlabel('Time from Go cue (s)')
        
        if save:
            plt.savefig(self.path + r'contra_ipsi_SDR_table.png')
        
        plt.show()

    def plot_three_selectivity(self,save=False):
        
        f, axarr = plt.subplots(1,5, sharex='col', figsize=(21,5))
        
        epochs = [range(self.time_cutoff), range(8,14), range(19,28), range(29,self.time_cutoff)]
        x = np.arange(-5.97,4,0.2)[:self.time_cutoff]
        titles = ['Whole-trial', 'Sample', 'Delay', 'Response']
        
        num_epochs = []
        
        for i in range(4):
            
            contra_neurons, ipsi_neurons, contra_trace, ipsi_trace = self.contra_ipsi_pop(epochs[i])
            
            if len(contra_neurons) == 0:
                
                nonpref, pref = ipsi_trace['r'], ipsi_trace['l']
                
            elif len(ipsi_neurons) == 0:
                nonpref, pref = contra_trace['l'], contra_trace['r']

            else:
                nonpref, pref = cat((ipsi_trace['r'], contra_trace['l'])), cat((ipsi_trace['l'], contra_trace['r']))
                
                
            sel = np.mean(pref, axis = 0) - np.mean(nonpref, axis = 0)
            
            err = np.std(pref, axis=0) / np.sqrt(len(pref)) 
            err += np.std(nonpref, axis=0) / np.sqrt(len(nonpref))
                        
            axarr[i + 1].plot(x, sel, 'b-')
                    
            axarr[i + 1].fill_between(x, sel - err, 
                      sel + err,
                      color=['#b4b2dc'])

            axarr[i + 1].set_title(titles[i])
            
            num_epochs += [len(contra_neurons) + len(ipsi_neurons)]

        # Bar plot
        axarr[0].bar(['S', 'D', 'R'], np.array(num_epochs[1:]) / sum(num_epochs[1:]), color = ['dimgray', 'darkgray', 'gainsboro'])
        
        axarr[0].set_ylim(0,1)
        axarr[0].set_title('Among all ALM neurons')
        
        axarr[0].set_ylabel('Proportion of neurons')
        axarr[1].set_ylabel('Selectivity')
        axarr[2].set_xlabel('Time from Go cue (s)')
        
        
        plt.show()
        
    def population_sel_timecourse(self, save=True):
        
        f, axarr = plt.subplots(2, 1, sharex='col', figsize=(20,15))
        epochs = [range(14,28), range(21,self.time_cutoff), range(29,self.time_cutoff)]
        x = np.arange(-5.97,4,0.2)[:self.time_cutoff]
        titles = ['Preparatory', 'Prep + response', 'Response']
        
        sig_n = dict()
        sig_n['c'] = []
        sig_n['i'] = []
        contra_mat = np.zeros(self.time_cutoff)
        ipsi_mat = np.zeros(self.time_cutoff)
        
        for i in range(3):
            
            # contra_neurons, ipsi_neurons, contra_trace, ipsi_trace = self.contra_ipsi_pop(epochs[i])
            
            for n in self.get_epoch_selective(epochs[i]):
                                
                r, l = self.get_trace_matrix(n)
                r, l = np.array(r), np.array(l)
                side = 'c' if np.mean(r[:, epochs[i]]) > np.mean(l[:,epochs[i]]) else 'i'
                
                r, l = np.mean(r,axis=0), np.mean(l,axis=0)
                
                if side == 'c' and n not in sig_n['c']:
                    
                    sig_n['c'] += [n]
    
                    contra_mat = np.vstack((contra_mat, r - l))

                if side == 'i' and n not in sig_n['i']:
                    
                    sig_n['i'] += [n]

                    ipsi_mat = np.vstack((ipsi_mat, l - r))

        axarr[0].matshow((ipsi_mat[1:]), aspect="auto", cmap='jet')
        axarr[0].set_title('Ipsi-preferring neurons')
        
        axarr[1].matshow(-(contra_mat[1:]), aspect="auto", cmap='jet')
        axarr[1].set_title('Contra-preferring neurons')
        
        if save:
            plt.savefig(self.path + r'population_selectivity_overtime.jpg')
        
        plt.show()


    def selectivity_optogenetics(self, save=False):
        
        f, axarr = plt.subplots(1,1, sharex='col', figsize=(5,5))
        
        x = np.arange(-5.97,4,0.2)[:self.time_cutoff]

        # Get delay selective neurons
        contra_neurons, ipsi_neurons, contra_trace, ipsi_trace = self.contra_ipsi_pop(range(19,28)) 
        
        if len(contra_neurons) == 0:
            
            nonpref, pref = ipsi_trace['r'], ipsi_trace['l']
            optonp, optop = self.get_trace_matrix_multiple(ipsi_neurons, opto=True, both=True)
            # errnp, errpref = self.get_trace_matrix_multiple(ipsi_neurons, opto=True, error=True)
            
        elif len(ipsi_neurons) == 0:
            
            nonpref, pref = contra_trace['l'], contra_trace['r']
            optop, optonp = self.get_trace_matrix_multiple(contra_neurons, opto=True, both=True)
            # errpref, errnp = self.get_trace_matrix_multiple(contra_neurons, opto=True, error=True)

        else:
            
            nonpref, pref = cat((ipsi_trace['r'], contra_trace['l'])), cat((ipsi_trace['l'], contra_trace['r']))
            optonp, optop = self.get_trace_matrix_multiple(ipsi_neurons, opto=True, both=True)
            optop1, optonp1 = self.get_trace_matrix_multiple(contra_neurons, opto = True, both=True)
            optonp, optop = cat((optonp, optonp1)), cat((optop, optop1))
            
            # errnp, errpref = self.get_trace_matrix_multiple(ipsi_neurons, opto=True, error=True)
            # errpref1, errnp1 = self.get_trace_matrix_multiple(contra_neurons, opto=True, error=True)
            # errpref, errnp = cat((errpref, errpref1)), cat((errnp, errnp1))

            
        sel = np.mean(pref, axis = 0) - np.mean(nonpref, axis = 0)
        err = np.std(pref, axis=0) / np.sqrt(len(pref)) 
        err += np.std(nonpref, axis=0) / np.sqrt(len(nonpref))
        
        selo = np.mean(optop, axis = 0) - np.mean(optonp, axis = 0)
        erro = np.std(optop, axis=0) / np.sqrt(len(optop)) 
        erro += np.std(optonp, axis=0) / np.sqrt(len(optonp))  

        axarr.plot(x, sel, 'black')
                
        axarr.fill_between(x, sel - err, 
                  sel + err,
                  color=['darkgray'])
        
        axarr.plot(x, selo, 'b-')
                
        axarr.fill_between(x, selo - erro, 
                  selo + erro,
                  color=['#b4b2dc'])       

        axarr.set_title('Optogenetic effect on selectivity')                  
        axarr.set_xlabel('Time from Go cue (s)')
        axarr.set_ylabel('Selectivity')
        # axarr[0].plot(x, sel, 'black')
                
        # axarr[0].fill_between(x, sel - err, 
        #           sel + err,
        #           color=['darkgray'])
        
        # axarr[0].plot(x, selo, 'b-')
                
        # axarr[0].fill_between(x, selo - erro, 
        #           selo + erro,
        #           color=['#b4b2dc'])       

        # axarr[0].set_title('Optogenetic effect on selectivity')
        
        # selo = np.mean(errpref, axis = 0) - np.mean(errnp, axis = 0)
        # erro = np.std(errpref, axis=0) / np.sqrt(len(errpref)) 
        # erro += np.std(errnp, axis=0) / np.sqrt(len(errnp)) 
        
        # axarr[1].plot(x, sel, 'black')
                
        # axarr[1].fill_between(x, sel - err, 
        #           sel + err,
        #           color=['darkgray'])
        
        # axarr[1].plot(x, selo, 'b-')
                
        # axarr[1].fill_between(x, selo - erro, 
        #           selo + erro,
        #           color=['#b4b2dc'])   

        # axarr[1].set_title('Incorrect trials')
        
        if save:
            plt.savefig(self.path + r'opto_effect_on_selectivity.png')

        
        plt.show()
        
### Quality analysis section ###
        
    def all_neurons_heatmap(self, save=False):
        
        f, axarr = plt.subplots(2,2, sharex='col')
        # x = np.arange(-5.97,4,0.2)[:self.time_cutoff]

        stim_dff = self.dff[0][self.stim_ON]
        non_stim_dff = self.dff[0][~self.stim_ON]

        stack = np.zeros(self.time_cutoff)

        for neuron in range(stim_dff[0].shape[0]):
            dfftrial = []
            for trial in range(stim_dff.shape[0]):
                dfftrial += [stim_dff[trial][neuron, :self.time_cutoff]]

            stack = np.vstack((stack, np.mean(np.array(dfftrial), axis=0)))

        stack = normalize(stack[1:])
        axarr[0,0].matshow(stack, cmap='gray', interpolation='nearest', aspect='auto')
        axarr[0,0].axis('off')
        axarr[0,0].set_title('Opto')
        axarr[0,0].axvline(x=13, c='b', linewidth = 0.5)
        axarr[1,0].plot(np.mean(stack, axis = 0))
        axarr[1,0].set_ylim(top=0.2)
        axarr[1,0].axvline(x=13, c='b', linewidth = 0.5)

        stack = np.zeros(self.time_cutoff)

        for neuron in range(non_stim_dff[0].shape[0]):
            dfftrial = []
            for trial in range(non_stim_dff.shape[0]):
                dfftrial += [non_stim_dff[trial][neuron, :self.time_cutoff]]

            stack = np.vstack((stack, np.mean(np.array(dfftrial), axis=0)))

        stack = normalize(stack[1:])

        axarr[0,1].matshow(stack, cmap='gray', interpolation='nearest', aspect='auto')
        axarr[0,1].axis('off')
        axarr[0,1].set_title('Control')

        axarr[1,1].plot(np.mean(stack, axis = 0))
        axarr[1,1].set_ylim(top=0.2)
        axarr[1,0].set_ylabel('dF/F0')
        # axarr[1,0].set_xlabel('Time from Go cue (s)')

        if save:
            plt.savefig(self.path + r'dff_contra_stimall.jpg')

        plt.show()
    
        return None
    
    def all_neurons_heatmap_stimlevels(self, save=False):
        
        f, axarr = plt.subplots(2,6, sharex='col', figsize=(20,6))
        # x = np.arange(-5.97,4,0.2)[:self.time_cutoff]

        non_stim_dff = self.dff[0][self.stim_level == 0]
        
        for i in range(1, len(set(self.stim_level))):
            
            level = sorted(list(set(self.stim_level)))[i]
            stim_dff = self.dff[0][self.stim_level == level]
    
            stack = np.zeros(self.time_cutoff)
    
            for neuron in range(stim_dff[0].shape[0]):
                dfftrial = []
                for trial in range(stim_dff.shape[0]):
                    dfftrial += [stim_dff[trial][neuron, :self.time_cutoff]]
    
                stack = np.vstack((stack, np.mean(np.array(dfftrial), axis=0)))
    
            stack = normalize(stack[1:])
            axarr[0,i].matshow(stack, cmap='gray', interpolation='nearest', aspect='auto')
            axarr[0,i].axis('off')
            axarr[0,i].set_title('Opto {} AOM'.format(level))
            axarr[0,i].axvline(x=13, c='b', linewidth = 0.5)
            axarr[1,i].plot(np.mean(stack, axis = 0))
            axarr[1,i].set_ylim(top=0.2)
            axarr[1,i].axvline(x=13, c='b', linewidth = 0.5)

        stack = np.zeros(self.time_cutoff)

        for neuron in range(non_stim_dff[0].shape[0]):
            dfftrial = []
            for trial in range(non_stim_dff.shape[0]):
                dfftrial += [non_stim_dff[trial][neuron, :self.time_cutoff]]

            stack = np.vstack((stack, np.mean(np.array(dfftrial), axis=0)))

        stack = normalize(stack[1:])

        axarr[0,0].matshow(stack, cmap='gray', interpolation='nearest', aspect='auto')
        axarr[0,0].axis('off')
        axarr[0,0].set_title('Control')

        axarr[1,0].plot(np.mean(stack, axis = 0))
        axarr[1,0].set_ylim(top=0.2)
        axarr[1,0].set_ylabel('dF/F0')
        # axarr[1,0].set_xlabel('Time from Go cue (s)')

        if save:
            plt.savefig(self.path + r'dff_contra_stimall.jpg')

        plt.show()
    
        return None
    
    def stim_activity_proportion(self, save=False):
        
        stim_period = range(16,19)
        
        f, axarr = plt.subplots(1,5, sharex='col', figsize = (20, 4))
        # x = np.arange(-5.97,4,0.2)[:self.time_cutoff]
        
        control_neuron_dff = []
        opto_neuron_dff = []

        non_stim_dff = self.dff[0][self.stim_level == 0]
        
        for n in range(self.num_neurons):
            av = []
            
            for t in range(non_stim_dff.shape[0]):
                av += [non_stim_dff[t][n, 16:19]]
                
            control_neuron_dff += [np.mean(av)]
            
        
        for i in range(1, len(set(self.stim_level))):
            stimlevel = sorted(list(set(self.stim_level)))[i]
            stim_dff = self.dff[0][self.stim_level == stimlevel]
            level = []
            
            for n in range(self.num_neurons):
                av = []
                
                for t in range(stim_dff.shape[0]):
                    av += [stim_dff[t][n, 16:19]]
                    
                level += [np.mean(av)]
            
            opto_neuron_dff += [level]
            
        # for i in range(len(set(self.stim_level))-1):
            
            # ratio = [opto_neuron_dff[i-1][j] / control_neuron_dff[j] for j in range(len(control_neuron_dff))]
            ratio = [level[j] / control_neuron_dff[j] for j in range(len(control_neuron_dff))]
            ratio = np.array(ratio)[np.array(ratio) > -100]
            ratio = np.array(ratio)[np.array(ratio) < 100]

            axarr[i-1].scatter(control_neuron_dff, level)
 
            axarr[i-1].set_title('{} AOM'.format(stimlevel))
            # axarr[i-1].hist(ratio, bins = 500)
            # axarr[i-1].set_xlim(-10,10)
        axarr[0].set_ylabel('Opto level')
        axarr[2].set_xlabel('Control Level')
        plt.show()
        return control_neuron_dff, ratio