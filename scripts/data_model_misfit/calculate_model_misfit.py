# -*- coding: utf-8 -*-
"""
@author: Wenbin Jiang
"""
import os
import numpy as np
import math
from seisflows.plugins.solver_io.fortran_binary import _read

if __name__ == '__main__':

	# total iteration number
    Niter=20
    model_true_path = r'./../model_true'
    xcoord_name = model_true_path+'/'+'proc000000_x.bin'
    zcoord_name = model_true_path+'/'+'proc000000_z.bin'
    vp_true_name = model_true_path+'/'+'proc000000_vp.bin'
    vs_true_name = model_true_path+'/'+'proc000000_vs.bin'
    rho_true_name = model_true_path+'/'+'proc000000_rho.bin'
	
    if not os.path.exists(xcoord_name):
        print(xcoord_name)

    if not os.path.exists(zcoord_name):
        print(zcoord_name)

    x = _read(xcoord_name)
    z = _read(zcoord_name)
    vp_true = _read(vp_true_name)
    vs_true = _read(vs_true_name)
    rho_true = _read(rho_true_name)

    if os.path.exists('vp_misfit'):
        os.remove('vp_misfit')
    if os.path.exists('vs_misfit'):
        os.remove('vs_misfit')
    if os.path.exists('rho_misfit'):
        os.remove('rho_misfit')

    # read inverted model
    for iternum in range(Niter):
        model_inv_path = r'./../output'
        iternum_temp=iternum+1
        iter_temp = '%04d' % iternum_temp
        vp_inv_name = model_inv_path+'/'+'model_'+iter_temp+'/'+'proc000000_vp.bin'
        vs_inv_name = model_inv_path+'/'+'model_'+iter_temp+'/'+'proc000000_vs.bin'
        rho_inv_name = model_inv_path+'/'+'model_'+iter_temp+'/'+'proc000000_rho.bin'
        vp_inv = _read(vp_inv_name)
        vs_inv = _read(vs_inv_name)
        rho_inv = _read(rho_inv_name)
        #print(vp_inv[0]) 
		# calculate model misfit    
        vp_diff = vp_inv-vp_true
        vs_diff = vs_inv-vs_true
        rho_diff = rho_inv-rho_true
        #print(vp_diff) 

        vp_diff2 = vp_diff**2
        vs_diff2 = vs_diff**2
        rho_diff2 = rho_diff**2
        #print(vp_diff2) 

        vp_diff2_sum_ave_sqrt = math.sqrt(sum(vp_diff2)/len(vp_true))
        vs_diff2_sum_ave_sqrt = math.sqrt(sum(vs_diff2)/len(vp_true))
        rho_diff2_sum_ave_sqrt = math.sqrt(sum(rho_diff2)/len(vp_true))

        file=open('vp_misfit','a')
        file.write(str(vp_diff2_sum_ave_sqrt)+'\n')
        file.close()

        file=open('vs_misfit','a')
        file.write(str(vs_diff2_sum_ave_sqrt)+'\n')
        file.close()

        file=open('rho_misfit','a')
        file.write(str(rho_diff2_sum_ave_sqrt)+'\n')
        file.close()


