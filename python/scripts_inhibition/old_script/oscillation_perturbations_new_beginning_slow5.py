'''
Created on Aug 12, 2013

@author: lindahlm
'''


from core.network.default_params import Perturbation_list as pl
import numpy
import pprint
from core_old.toolbox import misc
from oscillation_perturbations_new_beginning_slow0 import get_solution
pp=pprint.pprint

d0=0.8
f_beta_rm=lambda f: (1-f)/(d0+f*(1-d0))

def STN_ampa_gaba_input_magnitude():
    l=[
       [20, 188, 0.08], # 20 Hz 
#        [20, 210, 0.08], # 20 Hz 
#        [25, 290, 0.119], #25 Hz
#        [30, 430, 0.18],      #30 Hz
#        [35, 540, 0.215],     #35 Hz,
#        [40, 702, 0.28],     #40 Hz
#        [45, 830., 0.336],   #45 Hz 
#        [46, 876.7, 0.349],  #46 Hz
#        [50, 1000.8, 0.3957],     # 50 Hz
#        [55, 1159., 0.458],  #50 Hz
#        [80, 2102, 0.794] # 80 Hz] 
       ]
    
    return l

def get():
    
    
    l=[]
    solution=get_solution()

    d={}
    misc.dict_update(d, solution['mul'])
    l+=[pl(d, '*', **{'name':''})]
      
    d={}
    misc.dict_update(d, solution['equal']) 
    l[-1]+=pl(d, '=', **{'name':'control_sim'}) 
        
        
    r_EI=[1000, 1600] #range(1000, 1200, 50)+range(1550, 1900, 50)
    r_EA=range(100, 1500, 100)
    r_CS=[180,250]
    w_STGA=numpy.linspace(1, 0.0, 15)
    
    
    agg=[[r0,r1,r2,w] for r0, r2 in zip(r_EI, r_CS) for r1 in r_EA for w in w_STGA]
    
    for rEI, rEA, rCS, w in agg:
        rEI=float(rEI)
        rEA=float(rEA)
        rCS=float(rCS)
        w=float(w)
        
        d={}
        misc.dict_update(d, solution['mul'])
        d['nest']['ST_GA_ampa']['weight']*=w
        l+=[pl(d, '*', **{'name':''})]
          
        d={}
        misc.dict_update(d, solution['equal']) 
        d['node']['EI']['rate']=rEI
        d['node']['EA']['rate']=rEA
        
        misc.dict_update(d, {'node':{'CS':{'rate':rCS}}}) 
        
        
        s='rEI_{0}_rEA_{1}_rCS_{2}_STGAw_{3}'.format(rEI, rEA, rCS, round(w,2) )
        
        l[-1]+=pl(d, '=', **{'name':s})   


    return l

l=get()
for i, p in enumerate(l):
    print i, p