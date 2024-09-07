# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 16:45:18 2024

@author: catherinewang

Code for cluster correlation matrix from https://wil.yegelwel.com/cluster-correlation-matrix/
"""
import sys
sys.path.append("C:\scripts\Imaging analysis")
import numpy as np
import scipy.io as scio
import matplotlib.pyplot as plt
from alm_2p.session import Session
from activityMode import Mode
from matplotlib.pyplot import figure
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import davies_bouldin_score
import stats
from numpy.linalg import norm
import seaborn as sns
from scipy.cluster.hierarchy import inconsistent
from sklearn.metrics import silhouette_score
from collections import Counter
import diptest

cat = np.concatenate
plt.rcParams['pdf.fonttype'] = '42' 

#%% Functions
def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def cos_sim(a,b):
    return np.dot(a, b)/(norm(a)*norm(b))

# Heatmap function
def plot_heatmap_across_sess(sess, neuron, return_arr=False):
    r, l = sess.get_trace_matrix(neuron)
    r, l = np.array(r), np.array(l)
        
    df = pd.DataFrame(r[:,range(sess.delay, sess.response)].T)  
    corrs = df.corr()
    
    df = pd.DataFrame(l[:,range(sess.delay, sess.response)].T)  
    l_corrs = df.corr()
    
    if return_arr:
        return corrs, l_corrs
    
    f = plt.figure(figsize = (5,5))
    plt.imshow(corrs)
    plt.xlabel('R trials')
    plt.title('Correlation of delay activity in R trials')
    plt.colorbar()   
    
    f = plt.figure(figsize = (5,5))
    plt.imshow(l_corrs)
    plt.xlabel('L trials')
    plt.title('Correlation of delay activity in L trials')
    plt.colorbar() 
    
    
import scipy
import scipy.cluster.hierarchy as sch

def cluster_corr(corr_array, inplace=False, both = False):
    """
    Rearranges the correlation matrix, corr_array, so that groups of highly 
    correlated variables are next to eachother 
    
    Parameters
    ----------
    corr_array : pandas.DataFrame or numpy.ndarray
        a NxN correlation matrix 
        
    Returns
    -------
    pandas.DataFrame or numpy.ndarray
        a NxN correlation matrix with the columns and rows rearranged
    """
    pairwise_distances = sch.distance.pdist(corr_array)
    linkage = sch.linkage(pairwise_distances, method='complete')
    cluster_distance_threshold = pairwise_distances.max()/2
    idx_to_cluster_array = sch.fcluster(linkage, cluster_distance_threshold, 
                                        criterion='distance')
    
    idx = np.argsort(idx_to_cluster_array)
    if len(set(idx_to_cluster_array)) == corr_array.shape[0]:
        sil_score, sil_score1 = 0, 2
    else:
        sil_score = silhouette_score(corr_array, idx_to_cluster_array)
    
        sil_score1 = davies_bouldin_score(corr_array, idx_to_cluster_array)
    
    # sil_score = inconsistent(linkage)
    
    if not inplace:
        corr_array = corr_array.copy()
    
    if isinstance(corr_array, pd.DataFrame):
        if both:
            return corr_array.iloc[idx, :].T.iloc[idx, :], idx_to_cluster_array, (sil_score, sil_score1)
        return corr_array.iloc[idx, :].T.iloc[idx, :]
    return corr_array[idx, :][:, idx]



#%% PATHS 

allpaths = [[    r'F:\data\BAYLORCW032\python\2023_10_05',
            # r'F:\data\BAYLORCW034\python\2023_10_12',
            r'F:\data\BAYLORCW036\python\2023_10_09',
            r'F:\data\BAYLORCW035\python\2023_10_26',
            r'F:\data\BAYLORCW037\python\2023_11_21',
            
            r'H:\data\BAYLORCW044\python\2024_05_22',
            r'H:\data\BAYLORCW044\python\2024_05_23',
            
            r'H:\data\BAYLORCW046\python\2024_05_29',
            r'H:\data\BAYLORCW046\python\2024_05_30',
            r'H:\data\BAYLORCW046\python\2024_05_31',
            ],

             [r'F:\data\BAYLORCW032\python\2023_10_19',
            # r'F:\data\BAYLORCW034\python\2023_10_22',
            r'F:\data\BAYLORCW036\python\2023_10_19',
            r'F:\data\BAYLORCW035\python\2023_12_07',
            r'F:\data\BAYLORCW037\python\2023_12_08',
            
            r'H:\data\BAYLORCW044\python\2024_06_06',
            r'H:\data\BAYLORCW044\python\2024_06_04',

            r'H:\data\BAYLORCW046\python\2024_06_07',
            r'H:\data\BAYLORCW046\python\2024_06_10',
            r'H:\data\BAYLORCW046\python\2024_06_11',
            ],


             [r'F:\data\BAYLORCW032\python\2023_10_24',
            # r'F:\data\BAYLORCW034\python\2023_10_27',
            r'F:\data\BAYLORCW036\python\2023_10_30',
            r'F:\data\BAYLORCW035\python\2023_12_15',
            r'F:\data\BAYLORCW037\python\2023_12_15',
            
            r'H:\data\BAYLORCW044\python\2024_06_19',
            r'H:\data\BAYLORCW044\python\2024_06_18',
            
            r'H:\data\BAYLORCW046\python\2024_06_24',
            r'H:\data\BAYLORCW046\python\2024_06_27',
            r'H:\data\BAYLORCW046\python\2024_06_26',
            
            ]]
#%% Run over learning

allnums_r = []
allavgs_r = []
allmaxs_r = []
allsils_r = []

allnums_l = []
allavgs_l = []
allmaxs_l = []
allsils_l = []

for i in range(3):
    
    nums_r = []
    avgs_r =[]
    maxs_r = []
    sils_r = []
    
    nums_l = []
    avgs_l =[]
    maxs_l = []
    sils_l = []
    
    for path in allpaths[i]:

        l1 = Session(path, use_reg = True, triple=True)
        
        # per neuron measurements
        num_clusters_l = []
        num_clusters_r = []

        max_clus_size_l = []
        max_clus_size_r = []

        av_clus_size_l = []
        av_clus_size_r = []
        
        all_sil_l = []
        all_sil_r = []

        for idx in range(len(l1.good_neurons)):

            rcorr, lcorr = plot_heatmap_across_sess(l1, l1.good_neurons[idx], return_arr=True)
            _, idmap_r, sil_r = cluster_corr(rcorr, both=True)
            _, idmap_l, sil_l = cluster_corr(lcorr, both=True)

            num_clusters_r += [len(set(idmap_r))]
            num_clusters_l += [len(set(idmap_l))]
            
            av_clus_size_r += [np.average(list(Counter(list(idmap_r)).values()))]
            av_clus_size_l += [np.average(list(Counter(list(idmap_l)).values()))]
            
            max_clus_size_r += [max(list(Counter(list(idmap_r)).values()))]
            max_clus_size_l += [max(list(Counter(list(idmap_l)).values()))]
            
            all_sil_r += [sil_r[0]]
            all_sil_l += [sil_l[0]]
            
            
        nums_r += [np.mean(num_clusters_r)]
        avgs_r += [np.mean(av_clus_size_r)]
        maxs_r += [np.median(max_clus_size_r)]
        sils_r += [all_sil_r]
        
        nums_l += [np.mean(num_clusters_l)]
        avgs_l += [np.mean(av_clus_size_l)]
        maxs_l += [np.median(max_clus_size_l)]
        sils_l += [all_sil_l]

        
    allnums_r += [nums_r]
    allavgs_r += [avgs_r]
    allmaxs_r += [maxs_r]
    allsils_r += [sils_r]
    
    allnums_l += [nums_l]
    allavgs_l += [avgs_l]
    allmaxs_l += [maxs_l]
    allsils_l += [sils_l]
    
#%% Number of clusters
f = plt.figure(figsize = (5,5))

plt.bar(np.arange(3)-0.2, np.mean(allnums_r, axis=1), 0.4, color = 'b', label='Right trials', alpha=0.5)
plt.bar(np.arange(3)+0.2, np.mean(allnums_l, axis=1), 0.4, color='r', label='Left trials', alpha=0.5)
for i in range(3):
    plt.scatter(np.ones(len(allnums_r[i])) * i - 0.2, allnums_r[i], color= 'b')
    plt.scatter(np.ones(len(allnums_l[i])) * i + 0.2, allnums_l[i], color ='r')
plt.ylabel('Average number of clusters')
plt.xticks(range(3), ['Naive', 'Learning' , 'Expert'])
plt.title('Average number of clusters per FOVs over learning')


#%% Avg size of clusters
f = plt.figure(figsize = (5,5))

plt.bar(np.arange(3)-0.2, np.mean(allavgs_r, axis=1), 0.4, color = 'b', label='Right trials', alpha=0.5)
plt.bar(np.arange(3)+0.2, np.mean(allavgs_l, axis=1), 0.4, color='r', label='Left trials', alpha=0.5)
for i in range(3):
    plt.scatter(np.ones(len(allavgs_r[i])) * i - 0.2, allavgs_r[i], color= 'b')
    plt.scatter(np.ones(len(allavgs_l[i])) * i + 0.2, allavgs_l[i], color ='r')
plt.ylabel('Average mean size of clusters')
plt.xticks(range(3), ['Naive', 'Learning' , 'Expert'])
plt.title('Average size of clusters per FOVs over learning')



#%% Max size of clusters
f = plt.figure(figsize = (5,5))

plt.bar(np.arange(3)-0.2, np.mean(allmaxs_r, axis=1), 0.4, color = 'b', label='Right trials', alpha=0.5)
plt.bar(np.arange(3)+0.2, np.mean(allmaxs_l, axis=1), 0.4, color='r', label='Left trials', alpha=0.5)
for i in range(3):
    plt.scatter(np.ones(len(allmaxs_r[i])) * i - 0.2, allmaxs_r[i], color= 'b')
    plt.scatter(np.ones(len(allmaxs_l[i])) * i + 0.2, allmaxs_l[i], color ='r')
plt.ylabel('Median max size of clusters')
plt.xticks(range(3), ['Naive', 'Learning' , 'Expert'])
plt.title('Maximum size (FOV med.) of clusters per FOVs over learning')

#%% Measures of clusters test


num_clusters_l = []
num_clusters_r = []

max_clus_size_l = []
max_clus_size_r = []

av_clus_size_l = []
av_clus_size_r = []

all_sil_r = []
all_sil_l = []

path = learningpath
n=15
l1 = Mode(path, use_reg = True, triple=True, baseline_normalization="median_zscore")

for idx in range(len(l1.good_neurons)):

    rcorr, lcorr = plot_heatmap_across_sess(l1, l1.good_neurons[idx], return_arr=True)
    _, idmap_r, sil_r = cluster_corr(rcorr, both=True)
    _, idmap_l, sil_l = cluster_corr(lcorr, both=True)

    num_clusters_r += [len(set(idmap_r))]
    num_clusters_l += [len(set(idmap_l))]
    
    av_clus_size_r += [np.average(list(Counter(list(idmap_r)).values()))]
    av_clus_size_l += [np.average(list(Counter(list(idmap_l)).values()))]
    
    max_clus_size_r += [max(list(Counter(list(idmap_r)).values()))]
    max_clus_size_l += [max(list(Counter(list(idmap_l)).values()))]
    
    all_sil_r += [sil_r]
    all_sil_l += [sil_l]

all_sil_r = np.array(all_sil_r)
all_sil_l = np.array(all_sil_l)
#%% Look at scores across the whole population of neurons

f = plt.figure(figsize = (5,5))
plt.hist(all_sil_r[:,0], bins=25, alpha=0.5, color='b', label='right trials')
plt.hist(all_sil_l[:,0], bins=25, alpha=0.5, color='r', label='left trials')
plt.legend()
plt.axvline(np.median(all_sil_r[:,0]), color='b')
plt.axvline(np.mean(all_sil_r[:,0]), color='b', ls='--')
plt.axvline(np.median(all_sil_l[:,0]), color='r')
plt.axvline(np.mean(all_sil_l[:,0]), color='r', ls='--')
# plt.xlabel('Davies-Bouldin score')
plt.xlabel('Silhouette score')
plt.title('Distribution of Silhouette scores for clusters across neurons')

print(diptest.diptest(np.array(all_sil_r)))
print(diptest.diptest(np.array(all_sil_l)))

#%% Look at scores of individual neurons
idx=225
l1.plot_rasterPSTH_sidebyside(l1.good_neurons[idx])
plot_heatmap_across_sess(l1, l1.good_neurons[idx])
rcorr, lcorr = plot_heatmap_across_sess(l1, l1.good_neurons[idx], return_arr=True)
_, idmap_r, sil_r = cluster_corr(rcorr, both=True)
_, idmap_l, sil_l = cluster_corr(lcorr, both=True)
f = plt.figure(figsize = (6,5))
sns.heatmap(cluster_corr(rcorr))
f = plt.figure(figsize = (6,5))
sns.heatmap(cluster_corr(lcorr))
print(sil_r, sil_l)

#%% Compare the scores across other measures - number of clusters vs score
f = plt.figure(figsize = (5,5))
plt.scatter(all_sil_l[:, 0], num_clusters_l, color='r')
plt.scatter(all_sil_r[:, 0], num_clusters_r, color='b')
plt.xlabel('Silhouette scores')
plt.ylabel('Number of clusters')

f = plt.figure(figsize = (5,5))
plt.scatter(all_sil_l[:, 0], av_clus_size_l, color='r')
plt.scatter(all_sil_r[:, 0], av_clus_size_r, color='b')
plt.xlabel('Silhouette scores')
plt.ylabel('Avg cluster size')


f = plt.figure(figsize = (5,5))
plt.scatter(all_sil_l[:, 0], max_clus_size_l, color='r')
plt.scatter(all_sil_r[:, 0], max_clus_size_r, color='b')
plt.xlabel('Silhouette scores')
plt.ylabel('Max cluster size')


f = plt.figure(figsize = (5,5))
plt.scatter(all_sil_l[:, 1], num_clusters_l, color='r')
plt.scatter(all_sil_r[:, 1], num_clusters_r, color='b')
plt.xlabel('Davies-Bouldin scores')
plt.ylabel('Number of clusters')

f = plt.figure(figsize = (5,5))
plt.scatter(all_sil_l[:, 1], av_clus_size_l, color='r')
plt.scatter(all_sil_r[:, 1], av_clus_size_r, color='b')
plt.xlabel('Davies-Bouldin scores')
plt.ylabel('Avg cluster size')


f = plt.figure(figsize = (5,5))
plt.scatter(all_sil_l[:, 1], max_clus_size_l, color='r')
plt.scatter(all_sil_r[:, 1], max_clus_size_r, color='b')
plt.xlabel('Davies-Bouldin scores')
plt.ylabel('Max cluster size')


#%% Compare the two scores with each other
f = plt.figure(figsize = (5,5))

all_sil_r = np.array(all_sil_r)
all_sil_l = np.array(all_sil_l)
plt.scatter(all_sil_r[:, 0], all_sil_r[:, 1],color='b')
plt.scatter(all_sil_l[:, 0], all_sil_l[:, 1],color='r')
plt.xlabel('Silhouette scores')
plt.ylabel('Davies-Bouldin scores')

#%% Now compare silh score with variance and weight

f = plt.figure(figsize = (5,5))

plt.scatter(np.log(allr), all_sil_r[:, 0],color='b')
plt.scatter(np.log(allr), all_sil_l[:, 0],color='r')
plt.ylabel('Goodness of cluster (silhouette score)')
plt.xlabel('Variance of weights (log)')
plt.title('Goodness of trial clustering and variance of CD_choice weights')
print(scipy.stats.pearsonr(np.log(allr), all_sil_r[:, 0]))
print(scipy.stats.pearsonr(np.log(allr), all_sil_l[:, 0]))


f = plt.figure(figsize = (5,5))

plt.scatter(np.abs(avg_weights), all_sil_r[:, 0],color='b')
plt.scatter(np.abs(avg_weights), all_sil_l[:, 0],color='r')
plt.ylabel('Goodness of cluster (silhouette score)')
plt.xlabel('Weight (abs)')
plt.title('Goodness of trial clustering and CD_choice weights')
print(scipy.stats.pearsonr(avg_weights, all_sil_r[:, 0]))
print(scipy.stats.pearsonr(avg_weights, all_sil_l[:, 0]))

#%% Silh score over learning all neurons
# Make df object to plot

df = pd.DataFrame()
df['score'] = cat(allsils_l[0])
df['Stage'] = 'Naive'
df['Trial'] = 'Left'

df1 = pd.DataFrame()
df1['score'] = cat(allsils_l[1])
df1['Stage'] = 'Learning'
df1['Trial'] = 'Left'

df2 = pd.DataFrame()
df2['score'] = cat(allsils_l[2])
df2['Stage'] = 'Expert'
df2['Trial'] = 'Left'

all_df = pd.concat((df,df1,df2))

df = pd.DataFrame()
df['score'] = cat(allsils_r[0])
df['Stage'] = 'Naive'
df['Trial'] = 'Right'

df1 = pd.DataFrame()
df1['score'] = cat(allsils_r[1])
df1['Stage'] = 'Learning'
df1['Trial'] = 'Right'

df2 = pd.DataFrame()
df2['score'] = cat(allsils_r[2])
df2['Stage'] = 'Expert'
df2['Trial'] = 'Right'

all_df = pd.concat((all_df, df, df1, df2))

# sns.violinplot(data=all_df, x='Stage', y='score', hue='Trial', split=True, inner="quart")
# plt.ylim(top=0.25)

sns.violinplot(data=all_df, x='Stage', y='score', hue='Trial', fill=False, inner="quart")
plt.ylim(top=0.25)
#%% Silh score over learning av over fov

f = plt.figure(figsize = (5,5))
plt.bar(np.arange(3)-0.2, [np.mean(cat(s)) for s in allsils_r], 0.4, color='b', alpha=0.5)
plt.bar(np.arange(3)+0.2, [np.mean(cat(s)) for s in allsils_l], 0.4, color='r', alpha=0.5)
for i in range(3):
    plt.scatter(np.ones(len(allsils_r[i])) * i - 0.2, [np.mean((s)) for s in allsils_r[i]], color = 'b')
    plt.scatter(np.ones(len(allsils_l[i])) * i + 0.2, [np.mean((s)) for s in allsils_l[i]], color = 'r')
    
plt.xticks(range(3), ['Naive', 'Learning', 'Expert'])
plt.ylabel('Av. silhouette score')
plt.title('Average silhouette score per FOV over learning')


#%%Correlate robustness with silh score

# susc = l1.susceptibility()

# Susceptibility
f = plt.figure(figsize = (5,5))
plt.scatter(susc, all_sil_r[:,0], color='b')
plt.scatter(susc, all_sil_l[:, 0], color='r')
plt.xlabel('Susceptibility')
plt.ylabel('Silhouette score')
plt.title('Susceptibility vs silhouette score: all neurons')
print(scipy.stats.pearsonr(susc, all_sil_r[:, 0]))
print(scipy.stats.pearsonr(susc, all_sil_l[:, 0]))

#%% Robustness
# rob = l1.modularity_proportion_per_neuron()
f = plt.figure(figsize = (5,5))
# plt.scatter(np.log(np.abs(rob)), all_sil_r[:,0], color='b')
# plt.scatter(np.log(np.abs(rob)), all_sil_l[:, 0], color='r')
plt.scatter((rob), all_sil_r[:,0], color='b')
plt.scatter((rob), all_sil_l[:, 0], color='r')
plt.xlabel('Log(Abs(Robustness))')
plt.ylabel('Silhouette score')
plt.title('Robustness vs silhouette score: all neurons')
print(scipy.stats.pearsonr(np.log(np.abs(rob)), all_sil_r[:, 0]))
print(scipy.stats.pearsonr(np.log(np.abs(rob)), all_sil_l[:, 0]))
#%% Modularity
# rob = l1.modularity_proportion_per_neuron(period=range(l1.delay, l1.delay + int(1/l1.fs)))
f = plt.figure(figsize = (5,5))
plt.scatter(np.log(np.abs(rob)), all_sil_r[:,0], color='b')
plt.scatter(np.log(np.abs(rob)), all_sil_l[:, 0], color='r')
plt.xlabel('Modularity (log(abs))')
plt.ylabel('Silhouette score')
plt.title('Robustness vs silhouette score: all neurons')
print(scipy.stats.pearsonr(np.log(np.abs(rob)), all_sil_r[:, 0]))
print(scipy.stats.pearsonr(np.log(np.abs(rob)), all_sil_l[:, 0]))
