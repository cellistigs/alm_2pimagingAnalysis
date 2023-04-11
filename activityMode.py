# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 11:42:45 2023

@author: Catherine Wang
"""
import numpy as np
from numpy import concatenate as cat
import matplotlib.pyplot as plt
from scipy import stats
import copy
import scipy.io as scio
from sklearn.preprocessing import normalize
from session import Session
import sympy

class Mode(Session):
    
    def __init__(self, path, layer_num, time_epochs = [7, 13, 28]):
        # Inherit all parameters and functions of session.py
        super().__init__(self, path, layer_num) 
        
    
    def basis_col(self, A):
        # Bases
    
        # basis_col(A) produces a basis for the subspace of Eucldiean n-space 
        # spanned by the vectors {u1,u2,...}, where the matrix A is formed from 
        # these vectors as its columns. That is, the subspace is the column space 
        # of A. The columns of the matrix that is returned are the basis vectors 
        # for the subspace. These basis vectors will be a subset of the original 
        # vectors. An error is returned if a basis for the zero vector space is 
        # attempted to be produced.
    
        # For example, if the vector space V = span{u1,u2,...}, where u1,u2,... are
        # row vectors, then set A to be [u1' u2' ...].
    
        # For example, if the vector space V = Col(B), where B is an m x n matrix,
        # then set A to be equal to B.
    
        matrix_size = np.shape(A)
    
        m = matrix_size[0]
        n = matrix_size[1]
    
        if np.array_equal(A, np.zeros((m,n))):
            raise ValueError('There does not exist a basis for the zero vector space.')
        elif n == 1:
            basis = A
        else:
            flag = 0
    
            if n == 2:
                multiple = A[0,1]/A[0,0]
                count = 0
    
                for i in range(m):
                    if A[i,1]/A[i,0] == multiple:
                        count = count + 1
    
                if count == m:
                    basis = A[:,0].reshape(-1, 1)
                    flag = 1
    
            if flag == 0:
                ref_A, pivot_columns = sympy.Matrix(A).rref() # double check if works
    
                B = np.zeros((m, len(pivot_columns)))
    
                for i in range(len(pivot_columns)):
                    B[:,i] = A[:,pivot_columns[i]]
    
                basis = B
    
        return basis
    
    def is_orthogonal_set(self, A):
        """
        Orthogonal Sets
    
        Determines if a set of vectors in Euclidean n-space is orthogonal. The matrix A
        is formed from these vectors as its columns. That is, the subspace spanned by the
        set of vectors is the column space of A. The value 1 is returned if the set is
        orthogonal. The value 0 is returned if the set is not orthogonal.
    
        For example, if the set of row vectors (u1, u2, ...) is to be determined for
        orthogonality, set A to be equal to np.array([u1, u2, ...]).T.
        """
        matrix_size = A.shape
        n = matrix_size[1]
        tolerance = 1e-10
    
        if n == 1:
            return 1
        else:
            G = A.T @ A - np.eye(n)
            if np.max(np.abs(G)) <= tolerance:
                return 1
            else:
                return 0
    
    def is_orthonormal_set(A):
        """
        Orthonormal Sets
    
        Determines if a set of vectors in Euclidean n-space is orthonormal. The matrix A
        is formed from these vectors as its columns. That is, the subspace spanned by the
        set of vectors is the column space of A. The value 1 is returned if the set is
        orthonormal. The value 0 is returned if the set is not orthonormal. An error is
        returned if a set containing only zero vectors is attempted to be determined for
        orthonormality.
    
        For example, if the set of row vectors (u1, u2, ...) is to be determined for
        orthonormality, set A to be equal to np.array([u1, u2, ...]).T.
        """
        matrix_size = A.shape
        m = matrix_size[0]
        n = matrix_size[1]
        tolerance = 1e-10
    
        if np.allclose(A, np.zeros((m, n))):
            raise ValueError('The set that contains just zero vectors cannot be orthonormal.')
        elif n == 1:
            if np.abs(np.linalg.norm(A[:, 0]) - 1) <= tolerance:
                return 1
            else:
                return 0
        else:
            if self.is_orthogonal_set(A) == 1:
                length_counter = 0
                for i in range(n):
                    if np.abs(np.linalg.norm(A[:, i]) - 1) <= tolerance:
                        length_counter += 1
    
                if length_counter == n:
                    return 1
                else:
                    return 0
            else:
                return 0



        
    def Gram_Schmidt_process(A):
        """
        Gram-Schmidt Process
        
        Gram_Schmidt_process(A) produces an orthonormal basis for the subspace of
        Eucldiean n-space spanned by the vectors {u1,u2,...}, where the matrix A 
        is formed from these vectors as its columns. That is, the subspace is the
        column space of A. The columns of the matrix that is returned are the 
        orthonormal basis vectors for the subspace. An error is returned if an
        orthonormal basis for the zero vector space is attempted to be produced.
    
        For example, if the vector space V = span{u1,u2,...}, where u1,u2,... are
        row vectors, then set A to be [u1' u2' ...].
    
        For example, if the vector space V = Col(B), where B is an m x n matrix,
        then set A to be equal to B.
        """
        matrix_size = np.shape(A)
    
        m = matrix_size[0]
        n = matrix_size[1]
    
        if np.array_equal(A, np.zeros((m,n))):
            raise ValueError('There does not exist any type of basis for the zero vector space.')
        elif n == 1:
            orthonormal_basis = A[:, 0]/np.linalg.norm(A[:, 0])
        else:
            flag = 0
    
            if is_orthonormal_set(A) == 1:
                orthonormal_basis = A
                flag = 1
    
            if flag == 0:
                if np.linalg.matrix_rank(A) != n:
                    A = self.basis_col(A)
                
                matrix_size = np.shape(A)
                m = matrix_size[0]
                n = matrix_size[1]
    
                orthonormal_basis = A[:, 0]/np.linalg.norm(A[:, 0])
    
                for i in range(1, n):
                    u = A[:, i]
                    v = np.zeros((m, 1))
    
                    for j in range(i):
                        v -= np.dot(u, orthonormal_basis[:, j]) * orthonormal_basis[:, j]
    
                    v_ = u + v
                    orthonormal_basis[:, i] = v_/np.linalg.norm(v_)
    
        return orthonormal_basis
    
    def func_compute_activity_modes_DRT(PSTH_yes_correct, PSTH_no_correct, PSTH_yes_error, PSTH_no_error, T_cue_aligned_sel, time_epochs):
    
        # Inputs: Left Right Correct Error traces of ALL neurons that are selective
        #           time stamps for analysis?
        #           time epochs
        # Outputs: Orthonormal basis (nxn) where n = # of neurons
        #           activity variance of each dimension (nx1)
        
        # Actual method uses SVD decomposition
    
        t_sample = time_epochs[0]
        t_delay = time_epochs[1]
        t_response = time_epochs[2]
    
        activityRL = np.concatenate((PSTH_yes_correct, PSTH_no_correct), axis=1)
        activityRL = activityRL - np.mean(activityRL, axis=1, keepdims=True) # remove?
        u, s, v = np.linalg.svd(activityRL.T)
        proj_allDim = activityRL.T @ v
    
        # Variance of each dimension normalized
        var_s = np.square(np.diag(s[0:proj_allDim.shape[1], :]))
        var_allDim = var_s / np.sum(var_s)
    
        # Relevant choice dims
        CD_stim_mode = [] # Sample period
        CD_choice_mode = [] # Late delay period
        CD_outcome_mode = [] # Response period
        CD_sample_mode = [] # wt during the first 400 ms of the sample epoch
        CD_delay_mode = []
        CD_go_mode = []
        Ramping_mode = []
        GoDirection_mode = [] # To calculate the go direction (GD), we subtracted (rlick-right, t + rlick-left, t)/2 after the Go cue (Tgo < t < Tgo + 0.1 s) from that before the Go cue (Tgo - 0.1 s < t < Tgo), followed by normalization by its own norm. 

    
        wt = (PSTH_yes_correct + PSTH_yes_error) / 2 - (PSTH_no_correct + PSTH_no_error) / 2
        i_t = np.where((T_cue_aligned_sel[0, :] > t_sample) & (T_cue_aligned_sel[0, :] < t_delay))[0]
        CD_stim_mode = np.mean(wt[:, i_t], axis=1)
    
        wt = (PSTH_yes_correct + PSTH_no_error) / 2 - (PSTH_no_correct + PSTH_yes_error) / 2
        i_t = np.where((T_cue_aligned_sel[0, :] > t_delay) & (T_cue_aligned_sel[0, :] < t_response))[0]
        CD_choice_mode = np.mean(wt[:, i_t], axis=1)
    
        wt = (PSTH_yes_correct + PSTH_no_correct) / 2 - (PSTH_yes_error + PSTH_no_error) / 2
        i_t = np.where((T_cue_aligned_sel[0, :] > t_response) & (T_cue_aligned_sel[0, :] < (t_response + 1.3)))[0]
        CD_outcome_mode = np.mean(wt[:, i_t], axis=1)
    
        wt = PSTH_yes_correct - PSTH_no_correct
        
        i_t = np.where((T_cue_aligned_sel[0, :] > (t_sample + 0.2)) & (T_cue_aligned_sel[0, :] < (t_sample + 0.4)))[0]
        CD_sample_mode = np.mean(wt[:, i_t], axis=1)
    
        i_t = np.where((T_cue_aligned_sel[0, :] > (t_response - 0.3)) & (T_cue_aligned_sel[0, :] < (t_response - 0.1)))[0]
        CD_delay_mode = np.mean(wt[:, i_t], axis=1)
    
        i_t = np.where((T_cue_aligned_sel[0, :] > (t_response + 0.1)) & (T_cue_aligned_sel[0, :] < (t_response + 0.3)))[0]
        CD_go_mode = np.mean(wt[:, i_t], axis=1)
    
        wt = (PSTH_yes_correct + PSTH_no_correct)/2
        
        i_t1 = np.where((T_cue_aligned_sel[0, :] > (t_sample-0.3)) & (T_cue_aligned_sel[0, :] < (t_sample-0.1)))[0]
        i_t2 = np.where((T_cue_aligned_sel[0, :] > (t_response-0.3)) & (T_cue_aligned_sel[0, :] < (t_response-0.1)))[0]
        Ramping_mode = np.mean(wt[:, i_t2], axis=1) - np.mean(wt[:, i_t1], axis=1)
        
        i_t1 = np.where((T_cue_aligned_sel[0, :] > (t_response-0.1)) & (T_cue_aligned_sel[0, :] < t_response))[0]
        i_t2 = np.where((T_cue_aligned_sel[0, :] > t_response) & (T_cue_aligned_sel[0, :] < (t_response+0.1)))[0]
        GoDirction_mode = np.mean(wt[:, i_t2], axis=1) - np.mean(wt[:, i_t1], axis=1)
        
        CD_stim_mode = CD_stim_mode / np.linalg.norm(CD_stim_mode)
        CD_choice_mode = CD_choice_mode / np.linalg.norm(CD_choice_mode)
        CD_outcome_mode = CD_outcome_mode / np.linalg.norm(CD_outcome_mode)
        CD_sample_mode = CD_sample_mode / np.linalg.norm(CD_sample_mode)
        CD_delay_mode = CD_delay_mode / np.linalg.norm(CD_delay_mode)
        CD_go_mode = CD_go_mode / np.linalg.norm(CD_go_mode)
        Ramping_mode = Ramping_mode / np.linalg.norm(Ramping_mode)
        GoDirection_mode = GoDirection_mode / np.linalg.norm(GoDirction_mode)
        
        orthonormal_basis = Gram_Schmidt_process(np.concatenate((CD_stim_mode, CD_choice_mode, CD_outcome_mode, CD_sample_mode, CD_delay_mode, CD_go_mode, Ramping_mode, GoDirction_mode, v), axis=1))
        
        proj_allDim = np.dot(activityRL, orthonormal_basis)
        var_allDim = np.sum(proj_allDim**2, axis=0)
        
        var_allDim = var_allDim / np.sum(var_allDim)

    
    
    