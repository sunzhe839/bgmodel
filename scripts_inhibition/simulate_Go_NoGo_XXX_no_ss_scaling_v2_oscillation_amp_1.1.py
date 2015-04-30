'''
Created on Aug 12, 2013

@author: lindahlm
'''
from toolbox import monkey_patch as mp
mp.patch_for_milner()

from simulate import (pert_add_go_nogo_ss, get_path_logs, 
                      par_process_and_thread,
                      get_args_list_Go_NoGo_compete,
                      get_kwargs_list_indv_nets)
from toolbox.network import default_params
from toolbox.network.manager import Builder_Go_NoGo_with_lesion_FS_oscillation as Builder
from toolbox.parallel_excecution import loop
from toolbox import my_socket

import scripts_inhibition.Go_NoGo_compete as module

import sys
# from scripts inhibition import Go_NoGo_compete as module
import oscillation_perturbations41_slow as op
import pprint
pp=pprint.pprint

FILE_NAME=__file__.split('/')[-1][0:-3]
FROM_DISK_0=int(sys.argv[1]) if len(sys.argv)>1 else 0
proportion_connected=[0.1, 0.5, 1.]
NUM_RUNS=len(proportion_connected)
NUM_NETS=5
num_sims=NUM_NETS*NUM_RUNS

LOAD_MILNER_ON_SUPERMICRO=False


amp_base=1.1
freqs= 0.0
STN_amp_mod=3.

kwargs={
        
        'amp_base':amp_base,

        'Builder':Builder,
        
        'cores_milner':40*4,
        'cores_superm':40,
        
        'debug':False,
        'do_not_record':['M1', 'M2', 'FS','GA','GI', 'ST'], 
        'do_nets':['Net_'+str(i) for i in range(NUM_NETS)], #none means all
        'do_runs':range(NUM_RUNS),#range(NUM_RUNS), #none means all
        'do_obj':False,
        
        'file_name':FILE_NAME,
        'freqs':freqs,
        'freq_oscillations':20.,
        'from_disk_0':FROM_DISK_0,
        
        'i0':FROM_DISK_0,
        'input_type':'burst3_oscillations',
        
        'job_name':'Go_iso',

        'l_hours':['05','01','00'],
        'l_mean_rate_slices':['mean_rate_slices'],
        'l_minutes':['00','00','05'],
        'l_seconds':['00','00','00'],            
        'labels':['Only D1', 
                   'D1,D2',
                   'MSN lesioned (D1, D2)',
                   'FSN lesioned (D1, D2)',
                   'GPe TA lesioned (D1,D2)'],
         
        'local_threads_milner':40,
        'local_threads_superm':4,
                 
        'max_size':20000.,
        'module':module,
        
        'nets':['Net_{}'.format(i) for i in range(NUM_NETS)],
        
        'other_scenario':True, #channels (set-set) also in GPE-SNR
        
        'path_code':default_params.HOME_CODE,
        'path_results':get_path_logs(LOAD_MILNER_ON_SUPERMICRO, 
                                     FILE_NAME),
        'perturbation_list':[op.get()[5]],
        'proportion_connected':proportion_connected, #related to toal number fo runs
        
        'p_sizes':[1.]*NUM_RUNS,
        'p_subsamp':[1.]*NUM_RUNS,

        'STN_amp_mod':STN_amp_mod,
        }

if my_socket.determine_computer()=='milner':
    kw_add={
            'duration':[907.,100.0],            
            'laptime':1007.0,
            'res':10,
            'rep':40,
            'time_bin':100.,

            }
elif my_socket.determine_computer()=='supermicro':
    kw_add={
            'duration':[357., 100.0],
            'laptime':457.,
            'res':3, 
            'rep':5,
            'time_bin':1000/256.,
            }
kwargs.update(kw_add)

d_process_and_thread=par_process_and_thread(**kwargs)
kwargs.update(d_process_and_thread)

p_list=pert_add_go_nogo_ss(**kwargs)

for i, p in enumerate(p_list): print i, p

a_list=get_args_list_Go_NoGo_compete(p_list, **kwargs)
k_list=get_kwargs_list_indv_nets(len(p_list), kwargs)

loop(5, [num_sims,num_sims, NUM_RUNS], a_list, k_list )
        