'''
Created on Aug 12, 2013

@author: lindahlm
'''
from copy import deepcopy
from inhibition_gather_results import process
from core import misc
from core.network.default_params import Perturbation_list as pl
from core.network.manager import Builder_slow_wave2 as Builder
from core.parallel_excecution import loop

import numpy
import scripts_inhibition.base_oscillation_sw
import oscillation_perturbations as op
import pprint
pp=pprint.pprint


def perturbations():
    sim_time=20000.0
    size=20000.0
    threads=2

    path=('/home/mikael/results/papers/inhibition'+
       '/network/simulate_inhibition_ZZZ/')
    
    l=op.get()

    for i in range(len(l)):
        l[i]+=pl({'simu':{'sim_time':sim_time,
                          'sim_stop':sim_time,
                          'threads':threads},
                  'netw':{'size':size}},
                  '=')


    freqs=[0.5, 1.0, 1.5]
    
    damp=process(path, freqs)
    for key in sorted(damp.keys()):
        val=damp[key]
        print numpy.round(val, 2), key

    ll=[]
    for j in range(3):
        for i, _l in enumerate(l):
            amp=[numpy.round(damp[_l.name][j],2), 1]
            d={'type':'oscillation2', 
               'params':{'p_amplitude_mod':amp[0],
                         'p_amplitude0':amp[1],
                         'freq': 1.}} 
            _l=deepcopy(_l)
            dd={}
            for key in ['C1', 'C2', 'CF', 'CS']: 
                dd=misc.dict_update(dd, {'netw': {'input': {key:d} } })     
                      
            _l+=pl(dd,'=',**{'name':'amp_{0}-{1}'.format(*amp)})
                
            ll.append(_l)
        
        

    return ll, threads


p_list, threads=perturbations()
for i, p in enumerate(p_list):
    print i, p
args_list=[]
 

from os.path import expanduser
home = expanduser("~")
   
path=(home + '/results/papers/inhibition/network/'
      +__file__.split('/')[-1][0:-3]+'/')

n=len(p_list)


for j in range(2,3):
    for i, p in enumerate(p_list):
        
#         if i>=n-11:
# #         if i>18:
#             continue
#         if i<25:
#             continue
        
        from_disk=j

        fun=simulate_slow_wave.main
        script_name=(__file__.split('/')[-1][0:-3]+'/script_'+str(i)+'_'+p.name)
#         fun(*[Builder, from_disk, p, script_name, threads])
        args_list.append([fun,script_name]
                         +[Builder, from_disk, p, 
                           script_name, threads])


loop(args_list, path, 10)
        