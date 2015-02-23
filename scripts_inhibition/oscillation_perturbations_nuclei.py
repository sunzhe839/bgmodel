'''
Created on Aug 12, 2013

@author: lindahlm
'''


from toolbox.network.default_params import Perturbation_list as pl
from toolbox import misc
import pprint
pp=pprint.pprint

def get():
    
    def get_perturbation_dics(val, hz_mod, i):
        d = {}
#         for key in c.keys():
        for neuron, hz_pA in val:
            hz=hz_mod[neuron][i]
            u = {key:{'node':{neuron:{'I_vivo':1./hz_pA*hz}}}}
            d = misc.dict_update(d, u)
        return d
                
    c={
       'M1':[['M1',0.16]], #5/32 Hz/pA 
       'M2':[['M2',0.13]], #5/40 Hz/pA
       'FS':[['FS',0.17]], #10/60 Hz/pA
       'GP':[['GA',0.47],
             ['GI',0.47]], #0.47 Hz/pA
       'GA':[['GA',0.47]], #0.47 Hz/pA
       'GI':[['GI',0.47]], #0.47 Hz/pA
       'ST':[['ST',0.54]], #0.54 Hz/pA
       'SN':[['SN',0.16]]} #0.16 Hz/pA
    
       
    #in hz
    mod={'M1':[-8, -6,-4,-2, #  
                2, 4, 6, 8],
         'M2':[-8, -6,-4,-2, #  
                    2, 4, 6, 8],
         'FS':[-20, -15,-10,-5, #  
                5, 10, 15,-20 ],
         'GA':[-20, -15,-10,-5, #  
                5, 10, 15, 20 ],
         'GI':[-60, -45,-30,-15, #  
                15, 30, 45, 60],
         'ST':[-30, -22.5,-15,-7.5, #  
                7.5, 15, 22.5, 30 ],
         'SN':[-40, -30,-20,-10, #  
                10, 20, 30, 40]}
         
    l=[]
    
    l+=[pl(**{'name':'no_pert'})]
    
    for key, val in c.items():
        for i in range(8):
            
            d=get_perturbation_dics(val, mod, i)
            l.append(pl(d.values()[0],'+', **{'name':(key
                                          +'_pert_mod'
                                          +str(int(i)))}))
# neuron, hz_pA=val
#         for neuron, mods in mod.items():
#             for hz in mods:
#                 d=get_perturbation_dics({key:val}, mod, i)
#                 d={key:{'node':{neuron:{'I_vivo':1./hz_pA*hz}}}}
#                 
#                 l.append(pl(d.values()[0],'+', **{'name':(d.keys()[0]
#                                                           +'_pert_mod'
#                                                           +str(int(hz*hz_pA)))}))
#         
    return l 
 
if __name__=='__main__':
    get()
    pp(get())
 