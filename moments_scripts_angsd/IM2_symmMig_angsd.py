#!/usr/bin/env python

import matplotlib
matplotlib.use('PDF')
import moments
import random
import pylab
import matplotlib.pyplot as plt
import numpy as np
from numpy import array
from moments import Misc,Spectrum,Numerics,Manips,Integration,Demographics1D,Demographics2D
import sys
infile=sys.argv[1]
#pop_ids=[sys.argv[2],sys.argv[3]]
#projections=[int(sys.argv[4]),int(sys.argv[5])]
params=[float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6]),float(sys.argv[7]),float(sys.argv[8])]

# mutation rate per sequenced portion of genome per generation
mu=0.018
# generation time, in thousand years
gtime=0.005 

#dd = Misc.make_data_dict(infile)
#data = Spectrum.from_data_dict(dd, pop_ids,projections,polarized=False)

data = moments.Spectrum.from_file(infile)
nalleles=data.S()
print "N alleles: ",nalleles
ns=data.sample_sizes
np.set_printoptions(precision=3)     


#-------------------
# split with growth and asymmetrical migration
def IM2(params, ns):
    """
    Isolation-with-migration model with split into two arbtrary sizes
    symmetrical migration
    p_misid: proportion of misidentified ancestral states
    
    """
    nu1_0,nu2_0,nu1,nu2,T,mi,p_misid = params

    sts = moments.LinearSystem_1D.steady_state_1D(ns[0] + ns[1])
    fs = moments.Spectrum(sts)
    fs = moments.Manips.split_1D_to_2D(fs, ns[0], ns[1])

    nu1_func = lambda t: nu1_0 * (nu1/nu1_0)**(t/T)
    nu2_func = lambda t: nu2_0 * (nu2/nu2_0)**(t/T)
    nu_func = lambda t: [nu1_func(t), nu2_func(t)]
    fs.integrate(nu_func, T, dt_fac=0.01, m=np.array([[0, mi], [mi, 0]]))
    return (1-p_misid)*fs + p_misid*moments.Numerics.reverse_array(fs)

func=IM2
upper_bound = [100,100,100, 100, 10, 200,0.25]
lower_bound = [1e-3,1e-3,1e-3,1e-3, 1e-3,0.1,1e-5]
params = moments.Misc.perturb_params(params, fold=1, upper_bound=upper_bound,
                              lower_bound=lower_bound)

# fitting (poptg = optimal parameters):
poptg = moments.Inference.optimize_log(params, data, func,
                                   lower_bound=lower_bound,
                                   upper_bound=upper_bound,
                                   verbose=False,maxiter=10)
# extracting model predictions, likelihood and theta
model = func(poptg, ns)
ll_model = moments.Inference.ll_multinom(model, data)
theta = moments.Inference.optimal_sfs_scaling(model, data)

# random index for this replicate
ind=str(random.randint(0,999999))

# printing parameters and their SDs
print "IM2SM",ind,sys.argv[1],' ll: ', ll_model,' p: ', poptg, " t: ",theta,

moments.Plotting.plot_2d_comp_multinom(model, data, vmin=1, resid_range=3)
# plotting quad-panel figure wit AFS, model, residuals:
plt.savefig("IM2SM_"+ind+"_"+sys.argv[1]+'.pdf')
