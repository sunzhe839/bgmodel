'''
Created on Aug 12, 2013

@author: lindahlm
'''
import pythonpath #must be imported first
print 'before base_oscillation import'
from scripts_inhibition import base_oscillation
print 'after base_oscillation import'
import os

from core.network.manager import Builder_beta as Builder


import pprint
pp=pprint.pprint
    
DISPLAY=os.environ.get('DISPLAY')
THREADS=10

class Setup(object):

    def __init__(self, period, local_num_threads, **k):
        self.fs=256.
        self.local_num_threads=local_num_threads
        self.nets_to_run=k.get('nets_to_run', ['Net_0',
                                                'Net_1' ])
        self.period=period
       
  
    def builder(self):
        return {}
    
    def default_params(self):
        return {}
    
    def engine(self):
        d={'record':['spike_signal'],
           'verbose':True}
        return d
    
    def director(self):
        return {'nets_to_run':self.nets_to_run}  
    
    def activity_histogram(self):
        d = {'average':False,
             'period':self.period}
        
        return d

    def pds(self):
        d = {'NFFT':256, 'fs':self.fs, 
             'noverlap':256/2, 
             'local_num_threads':self.local_num_threads}
        return d
    
      
    def coherence(self):
        d = {'fs':self.fs, 
             'NFFT':128, 
            'noverlap':int(128/2), 
            'sample':100.**2, 
             'local_num_threads':self.local_num_threads,
             'min_signal_mean':0.0, #minimum mean a signal is alowed to have, toavoid calculating coherence for 0 signals
            'exclude_equal_signals':True, #do not compute for equal signals
   
             
             }
        return d
    

    def phase_diff(self):
        d = {'inspect':False, 
             'lowcut':15, 
             'highcut':25., 
             'order':3, 
             'fs':self.fs, 

             #Skip convolving when calculating phase shif
#              'bin_extent':int(self.fs/50),#20 for fs=1000.0 
#              'kernel_type':'gaussian', 
#              'params':{'std_ms':10., 
#                        'fs':self.fs}, 
             
             'local_num_threads':self.local_num_threads}
        
        return d

    def phases_diff_with_cohere(self):
        d={
            'fs':self.fs, 
            'NFFT':128, 
            'noverlap':int(128/2), 
            'sample':30.**2,  
            
            'lowcut':15, 
            'highcut':25., 
            'order':3, 
           
            'min_signal_mean':0.0, #minimum mean a signal is alowed to have, toavoid calculating coherence for 0 signals
            'exclude_equal_signals':True, #do not compute for equal signals
      
             #Skip convolving when calculating phase shif
#              'bin_extent':int(self.fs/50),#20., 
#              'kernel_type':'gaussian', 
#              'params':{'std_ms':10., 
#                        'fs':self.fs}, 
      
            'local_num_threads':self.local_num_threads}
        return d

    def firing_rate(self):
        d={'average':False, 
           'local_num_threads':self.local_num_threads,
#            'win':100.0,
           'time_bin':1000.0/self.fs}
        
        return d

    def plot_fr(self):
        d={'win':1.,
           't_start':5000.0,
           't_stop':6000.0,
           'labels':['Control', 'Lesion'],
           
           'fig_and_axes':{'n_rows':9, 
                            'n_cols':1, 
                            'w':800.0*0.55*2*0.3, 
                            'h':600.0*0.55*2*0.3, 
                            'fontsize':7,
                            'frame_hight_y':0.8,
                            'frame_hight_x':0.78,
                            'linewidth':1.}}
        return d


    def plot_coherence(self):
        d={'xlim':[0, 50],
           'statistics_mode':'activation'}
        return d
    
    def plot_summed(self):
        d={'xlim_cohere':[0, 50]}
        return d
    
    def plot_summed2(self):
        d={'xlim_cohere':[0, 50],
           'all':True,
           'p_95':False,
           'leave_out':['control_fr', 'control_cv'],
           'statistics_mode':'activation',
           'models_pdwc': ['GP_GP', 'GI_GI', 'GI_GA', 'GA_GA'],
           }
        return d

    def plot_summed_STN(self):
        d={'xlim_cohere':[0, 50],
           'all':True,
           'p_95':False,
           'leave_out':['control_fr', 'control_cv'],
           'statistics_mode':'activation',
           'models_pdwc': ['ST_ST', 'GP_ST', 'GI_ST', 'GA_ST'],
           }
        return d

    def plot_signals(self):
        d={ 
           'lowcut': 0.5,
           'highcut':1.5,
           'order':3,
           'fs':256.0, 
           'freq':20,
           't_start':5500.0,
           't_stop':6000.0,
           }
        return d

class Main():    
    def __init__(self, **kwargs):
        self.kwargs=kwargs
    
    def __repr__(self):
        return str(self.get_nets())+self.kwargs['script_name']

    
    def do(self):
        base_oscillation.main(**self.kwargs)

    def get_nets(self):
        return self.kwargs['setup'].nets_to_run

    def get_script_name(self):
        return self.kwargs['script_name']

    def get_name(self):
        nets='_'.join(self.get_nets()) 
        script_name=self.kwargs['script_name']
        script_name=script_name.split('/')[1].split('_')[0:2]
        script_name='_'.join(script_name)+'_'+nets
        return script_name+'_'+str(self.kwargs['from_disk'])
            
# def main(builder=Builder,
#          from_disk=2,
#          perturbation_list=None,
#          script_name=__file__.split('/')[-1][0:-3],
#          threads=10):
#     
# 
#  
# if __name__ == "__main__":
#     # stuff only to run when not called via 'import' here
#     main()



    