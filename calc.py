import os
import numpy as np
import numba
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from numba import prange
import glob
import sys



# Set the threading layer to workqueue (default)
os.environ['NUMBA_THREADING_LAYER'] = 'workqueue'

@numba.njit
def lorentz_dot(a, b):
    metric = np.array([-1, -1, -1, 1])  # Lorentzian metric signature (+, -, -, -)
    return np.dot(a * metric, b)

@numba.njit
def boost(vector, boost_v):
    bx, by, bz = boost_v[0], boost_v[1], boost_v[2]
    b2 = bx**2 + by**2 + bz**2
    ggamma = 1.0 / np.sqrt(1.0 - b2)
    bp = bx * vector[0] + by * vector[1] + bz * vector[2]
    gamma2 = (ggamma - 1.0) / b2

    vector[0] += gamma2 * bp * bx + ggamma * bx * vector[3]
    vector[1] += gamma2 * bp * by + ggamma * by * vector[3]
    vector[2] += gamma2 * bp * bz + ggamma * bz * vector[3]
    vector[3] = ggamma * (vector[3] + bp)
    
    return vector

@numba.njit(parallel=True)
def calcVariables(mom):
    mmu = 0.10566
    mp = 0.938
    ebeam = 120.0
    p_beam = np.array([0.0, 0.0, np.sqrt(ebeam * ebeam - mp * mp), ebeam])
    p_target = np.array([0.0, 0.0, 0.0, mp])
    p_cms = p_beam + p_target
    s = lorentz_dot(p_cms, p_cms)
    mass = np.zeros((len(mom)))
    pT = np.zeros((len(mom)))
    x1 = np.zeros((len(mom)))
    x2 = np.zeros((len(mom)))
    xF = np.zeros((len(mom)))
    costheta = np.zeros((len(mom)))
    sintheta = np.zeros((len(mom)))
    phi = np.zeros((len(mom)))
    for i in prange(len(mom)):
        momentum = mom[i]
        E_pos = np.sqrt(momentum[0] * momentum[0] + momentum[1] * momentum[1] + momentum[2] * momentum[2] + mmu * mmu)
        p_pos = np.array([momentum[0], momentum[1], momentum[2], E_pos])
        E_neg = np.sqrt(momentum[3] * momentum[3] + momentum[4] * momentum[4] + momentum[5] * momentum[5] + mmu * mmu)
        p_neg = np.array([momentum[3], momentum[4], momentum[5], E_neg])

        p_sum = p_pos + p_neg

        mass[i] = np.sqrt(lorentz_dot(p_sum, p_sum))
        pT[i] = np.sqrt(p_sum[0]**2 + p_sum[1]**2)

        x1[i] = lorentz_dot(p_target, p_sum) / lorentz_dot(p_target, p_cms)
        x2[i] = lorentz_dot(p_beam, p_sum) / lorentz_dot(p_beam, p_cms)
        
        costheta[i] = 2.0 * (p_neg[3] * p_pos[2] - p_pos[3] * p_neg[2]) / mass[i] / np.sqrt(mass[i] * mass[i] + pT[i] * pT[i])
        xF[i] = 2.0 * p_sum[2] / np.sqrt(s) / (1.0 - mass[i] * mass[i] / s)
        phi[i] = np.arctan2(2.0 * np.sqrt(mass[i] * mass[i] + pT[i] * pT[i]) * (p_neg[0] * p_pos[1] - p_pos[0] * p_neg[1]), 
                            mass[i] * (p_pos[0] * p_pos[0] - p_neg[0] * p_neg[0] + p_pos[1] * p_pos[1] - p_neg[1] * p_neg[1]))
        sintheta[i] = np.sqrt(1 - costheta[i]**2)
    return mass, pT, x1, x2, xF, costheta, sintheta, phi

