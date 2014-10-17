'''
Mikael Lindahl 2010


Module:
mynest

Here my own nest functions can be defined. For example connection functions
setting random weight or delay on connections.


'''

# Imports
import csv
import numpy
import numpy.random as rand

import socket
HOST=socket.gethostname().split('.')[0]
# if 'milner-login1.pdc.kth.se'==HOST:
# if 0:
from nest import *
import nest
import nest.pynestkernel as _kernel        

import time
from copy import deepcopy
from toolbox.parallelization import comm, Barrier
from toolbox.misc import Stopwatch

import pprint
pp=pprint.pprint

kernal_time=None

def SetKernelTime(t):
    global kernal_time
    kernal_time=t


def GetKernelTime():
    global kernal_time
    if kernal_time==None:
        return nest.GetKernelStatus('time')
    else:
        return kernal_time

def _Simulate_mpi(*args, **kwargs):
    with Barrier():
        print 'Simulating rank %i' % ( Rank()) #seems like it it neccesary to avoid hangup for mpi??!!
        nest.Simulate(*args, **kwargs)
        
def Simulate(*args, **kwargs):
    if comm.is_mpi_used():
        _Simulate_mpi(*args, **kwargs)    
    else:
        nest.Simulate(*args, **kwargs)   

def _Create_mpi(*args, **kwargs):
    with Barrier():
        return nest.Create(*args, **kwargs)
        
def Create(*args, **kwargs):
    if comm.is_mpi_used():
        return _Create_mpi(*args, **kwargs)    
    else:
        return nest.Create(*args, **kwargs)  


def Connect_DC(*args, **kwargs):
    if comm.is_mpi_used():
        _Connect_DC_mpi(*args, **kwargs)
    else:
        _Connect_DC(*args, **kwargs)
        
def _Connect_DC_mpi(*args, **kwargs):
    with Barrier():
        _Connect_DC(*args, **kwargs)

        
def _Connect_DC(pre, post, weights, delays, model):
    
    
    tp, receptor=nest.GetDefaults(model, ['type','receptor_type'])

    from itertools import izip
    with Stopwatch('Connecting DC', **{'only_rank_0_mpi':True}):   

        post_ids=list(numpy.unique(post))
        status=GetStatus(list(numpy.unique(post)), 'local')
        lock_up=dict(zip(post_ids,status))
        
        params=[{'delay': d,
               'receptor': receptor,
               'source': s,
               'synapse_model': model,
               'target': t,
               'type': tp,
               'weight': w}   for s, t, d, w, in izip(pre, 
                                                      post, 
                                                      delays, 
                                                      weights
                                                         )
               if lock_up[t]]


        DataConnect(params)
    del params

def Connect(*args, **kwargs):
    if comm.is_mpi_used():
        _Connect_mpi(*args, **kwargs)
    else:
        _Connect(*args, **kwargs)
        

def _Connect_mpi(*args, **kwargs):
    with Barrier():
        _Connect(*args, **kwargs)



def _Connect(pre, post, *args, **kwargs):

    def fun(pre, post, args, kwargs, sl):
        args=[a[sl] for a in args]
#         print sl
        if hasattr(nest, 'OneToOneConnect'):
            nest.OneToOneConnect(pre[sl], 
                                 post[sl],  
                                 *[a[sl] for a in args], **kwargs)
        else:
            nest.Connect(pre[sl], 
                         post[sl],  
                         *[a[sl] for a in args], **kwargs)
    
    chunks=kwargs.pop('chunks',1)
    n=len(pre)
    step=n/chunks
    
    slice_list=[]
    for i in range(chunks):
        if i<chunks-1:
            slice_list.append(slice(i*step,(i+1)*step))
        else:
            slice_list.append(slice(i*step, n))

    with Stopwatch('Connecting'):
        map(fun, [pre]*chunks, [post]*chunks, [args]*chunks,[kwargs]*chunks,slice_list)
         
#     if hasattr(nest, 'OneToOneConnect'):
#         nest.OneToOneConnect(pre, post,  *args, **kwargs)
#     else:
#         nest.Connect(pre, post,  *args, **kwargs)
 
#         if params:
#             syn_list=[{'model':model,
#                        'delay':delay,
#                        'weight':weight} 
#                       for delay, weight in zip(delay, params)]
#         else:
#             syn_list=[{'model':model}]*len(pre)
#         conn_list=[None]*len(pre)
#         
#         
#         pre=[[v] for v in pre] 
#         post=[[v] for v in post]
#         map(nest.Connect, pre, post, conn_list, syn_list) 
#         for source, target, syn_dict in zip(pre,  post, syn_list):
#             nest.Connect([source], [target], syn_spec=syn_dict)

def fun_pre_post(s,d,m):
    pushsli=_kernel.pushsli
    runsli=_kernel.runsli

    pushsli(s) #s
    pushsli(d) #d
    runsl('/{} Connect'.format(m))    
    
    
def fun_pre_post_params(*args):
    
    pushsli=_kernel.pushsli
    runsli=_kernel.runsli
    
    pushsli(args[0]) #s
    pushsli(args[1]) #d
    pushsli(args[2]) #p
    runsli('/%s Connect' % args[3])  
    
def fun_pre_post_weight_delay(*args):

    pushsli=_kernel.pushsli
    runsli=_kernel.runsli

    pushsli(args[0]) #s
    pushsli(args[1]) #d
    pushsli(args[2]) #w
    pushsli(args[3]) #dl
    runsli('/%s Connect' % args[4])                  



def _Connect_speed_internal(pre, post, params=None, delay=None, model="static_synapse"):
    """
    Make one-to-one connections of type model between the nodes in
    pre and the nodes in post. pre and post have to be lists of the
    same length. If params is given (as dictionary or list of
    dictionaries), they are used as parameters for the connections. If
    params is given as a single float or as list of floats, it is used
    as weight(s), in which case delay also has to be given as float or
    as list of floats.
    """


    if len(pre) != len(post):
        raise NESTError("pre and post have to be the same length")

    # pre post Connect
    if params == None and delay == None:
        map(connect_speed_fun.fun_pre_post, pre, post, [model]*len(pre))


    # pre post params Connect
    elif params != None and delay == None:
        params = broadcast(params, len(pre), (dict,), "params")
        if len(params) != len(pre):
            raise NESTError("params must be a dict, or list of dicts of length 1 or len(pre).")

        map(fun_pre_post_params, pre, post, params, [model]*len(pre))

    # pre post w d Connect
    elif params != None and delay != None:
        params = broadcast(params, len(pre), (float,), "params")
        if len(params) != len(pre):
            raise NESTError("params must be a float, or list of floats of length 1 or len(pre) and will be used as weight(s).")
        delay = broadcast(delay, len(pre), (float,), "delay")
        if len(delay) != len(pre):
            raise NESTError("delay must be a float, or list of floats of length 1 or len(pre).")
        
        map(fun_pre_post_weight_delay, pre, post, params, delay, [model]*len(pre))
        

    else:
        raise NESTError("Both 'params' and 'delay' have to be given.")


def _Connect_speed(pre, post, *args, **kwargs):

    def fun(pre, post, args, kwargs, sl):
        args=[a[sl] for a in args]
#         print sl

        _Connect_speed_internal(pre[sl], 
                         post[sl],  
                         *[a[sl] for a in args], **kwargs)
    
    chunks=kwargs.pop('chunks',1)
    n=len(pre)
    step=10000 #n/chunks
    
    slice_list=[]
    for i in range(chunks):
        if i<chunks-1:
            slice_list.append(slice(i*step,(i+1)*step))
        else:
            slice_list.append(slice(i*step, n))
    from toolbox.misc import Stopwatch
    with Stopwatch('Connecting'):
        map(fun, [pre]*chunks, [post]*chunks, [args]*chunks,[kwargs]*chunks,slice_list)

def Connect_speed(*args, **kwargs):
    if comm.is_mpi_used():
        _Connect_mpi(*args, **kwargs)
    else:
        _Connect_speed(*args, **kwargs)
        

def _Connect_speed_mpi(*args, **kwargs):
    with Barrier():
        _Connect_speed(*args, **kwargs)

def ConvergentConnect(pre, post, weight=None, delay=None, model="static_synapse"):
    """
    Connect all neurons in pre to each neuron in post. pre and post
    have to be lists. If weight is given (as a single float or as list
    of floats), delay also has to be given as float or as list of
    floats.
    """

    if weight == None and delay == None:
        for d in post :
            sps(pre)
            sps(d)
            sr('/%s ConvergentConnect' % model)

    elif weight != None and delay != None:
        weight = broadcast(weight, len(pre), (float,), "weight")
        if len(weight) != len(pre):
            raise NESTError("weight must be a float, or sequence of floats of length 1 or len(pre)")
        delay = broadcast(delay, len(pre), (float,), "delay")
        if len(delay) != len(pre):
            raise NESTError("delay must be a float, or sequence of floats of length 1 or len(pre)")
        
        for d in post:
            sps(pre)
            sps(d)
            sps(weight)
            sps(delay)
            sr('/%s ConvergentConnect' % model)

    else:
        raise NESTError("Both 'weight' and 'delay' have to be given.")


def collect_spikes_mpi(*args): 
    args=list(args)
    
    for i in range(len(args)):
        with Barrier():
            if comm.rank()==0:
                for i_proc in xrange(1, comm.size()):
                    args[i] = numpy.r_[args[i], 
                                       comm.recv(source=i_proc)]
                    
            else:
                comm.send(args[i],dest=0)
        args[i]=comm.bcast(args[i], root=0)
        
    return args

def _delete_data(path, **kwargs):
    for filename in sorted(os.listdir(path)):
        if filename.endswith(".gdf"):
            if kwargs.get('display', True):
                print 'Deleting: ' +path+'/'+filename
            os.remove(path+'/'+filename)    

def _delete_data_mpi(path, **kwargs):
    with Barrier():
        if comm.rank()==0:
            _delete_data(path, **kwargs)

def delete_data(path, **kwargs):
    if comm.is_mpi_used():
        return _delete_data_mpi(path, **kwargs)
    else:
        return _delete_data(path, **kwargs)

def get_spikes_from_memory(sd_id):
    e = GetStatus(sd_id)[0]['events'] # get events
    s = e['senders'] # get senders
    t = e['times'] # get spike times

    if comm.is_mpi_used():
        s,t=collect_spikes_mpi(s,t)    
    return s,t
            

def get_spikes_from_file(file_names):
    if comm.is_mpi_used():
        return _get_spikes_from_file_mpi(file_names)
    else:
        return _get_spikes_from_file(file_names)
    
def _get_spikes_from_file_mpi(file_names):
    with Barrier():
        if comm.rank()==0:
            data=_get_spikes_from_file(file_names)
        else:
            data=None
            
    with Barrier():        
        data=comm.bcast(data, root=0)
    return data
            
    
def _get_spikes_from_file(file_names):
    data=[]

#     if my_nest.Rank!=0:
#         return

    for name in file_names: 
        c=0
        while c<2:
            try:
                with open(name, 'rb') as csvfile:
                    csvreader = csv.reader(csvfile, delimiter='\t')
                    for row in csvreader:
                        data.append([float(row[0]), float(row[1])])
                c=2
            except:
                name_split=name.split('-')
                name=name_split[0]+'-0'+name_split[1]+'-'+name_split[2]
                c+=1
    data=numpy.array(data)
    if len(data):
        return data[:,0], data[:,1]
    else:
        return numpy.array([]), numpy.array([])

def GetThreads():
    if Rank()==1:
        return GetKernelStatus('local_num_threads') #shared memory
    else:
        return GetKernelStatus('num_processes') #mpi
        
   
def GetConn(soruces, targets):    
    c=[]
    
    for s in soruces:
        for t in targets:
            c.extend(nest.GetStatus(nest.FindConnections([s], [t])))     
    return c

def get_default_module_paths(home):

    if nest.version()=='NEST 2.2.2':
        s='nest-2.2.2'
    if nest.version()=='NEST 2.4.1':
        s='nest-2.4.1'    
    if nest.version()=='NEST 2.4.2':
        s='nest-2.4.2'   
          
    path= (home+'/opt/NEST/module/'
                  +'install-module-130701-'+s+'/lib/nest/ml_module')
    sli_path =(home+'/opt/NEST/module/'
                      +'install-module-130701-'+s+'/share/ml_module/sli')
    
    return path, sli_path

def install_module(path, sli_path, model_to_exist='my_aeif_cond_exp'):
    
    
    if not model_to_exist in nest.Models(): 
        nest.sr('('+sli_path+') addpath')
        nest.Install(path)
        

def GetConnProp(soruces, targets, prop_name, time):
    c=GetConn(soruces, targets)                                        
    x,y={},{}
    
    for conn in c:
        model=conn['synapse_model']
        
        if not model in y.keys():
            y[model]=[]
            x[model]=[]
            
        if prop_name in conn.keys():
            y[model].append(conn[prop_name])
        else:
            y[model].append(numpy.NaN)
            
        x[model].append(time)
    return x,y


def MyLoadModels( model_setup, models ):
    '''
    Input
        model_setup - list with tuples (base model, new model name, parameters)
                      or ddictionary with  keys  new model name and values
                      tuples  (base model, new model name, parameters)
        models     - new name of models in models to load into nest
    '''  
    if type(model_setup) in [list, tuple]:  
        for setup in model_setup: 
            if setup[ 1 ] in models:
                CopyModel( setup[ 0 ], setup[ 1 ], setup[ 2 ] )   # Create model
    elif type(model_setup)==dict:
        for model in models: 
            setup=model_setup[model]
            if not setup[ 1 ] in nest.Models():
                CopyModel( setup[ 0 ], setup[ 1 ], setup[ 2 ] )   # Create model
              

def MyCopyModel(params, new_name):
    
    params=deepcopy(params)
    type_id=params['type_id']
    del params['type_id']
    if not new_name in nest.Models():
        CopyModel( type_id, new_name, params ) 
    
        
def MySimulate(duration):

    print 'My simulate Rank %i' % ( Rank())
    start = time.time() 
    Simulate( duration )
    stop = time.time() 
    
    s = stop - start
    m = s // 60
    s = s - m*60
    print 'Rank %i simulation time: %i minutes, %i seconds' % ( Rank(), m, s )    

          
def ResetKernel(threads=1, print_time=False, display=False, **kwargs):

    
    if display:
        print 'Reseting kernel'
    nest.ResetKernel()
    #nest.SetKernelStatus({"resolution": .1, "print_time": print_time})
    nest.SetKernelStatus({ "print_time": print_time})
    
    n=nest.GetKernelStatus('total_num_virtual_procs')
    
    if n>1:
        nest.SetKernelStatus({"local_num_threads": 2})
        nest.SetKernelStatus({"local_num_threads":kwargs.get('threads_local',1)})
    else:    
        nest.SetKernelStatus({"local_num_threads":  threads})
    
    
    if 'data_path' in kwargs.keys():
        nest.SetKernelStatus({'data_path':kwargs.get('data_path')})

def sim_group(data_path,**kwargs):


    SetKernelStatus({"total_num_virtual_procs": kwargs.get("total_num_virtual_procs",4),
                     'data_path':data_path,
                     'overwrite_files':False})

    pg = Create("poisson_generator", params={"rate": 2000.0})
    n = Create('aeif_cond_exp', 10)
    sd = Create("spike_detector", params={"to_file": kwargs.get('to_file', True),
                                          "to_memory": kwargs.get('to_memory', False)})
    
    RandomConvergentConnect(pg, n, 100)
    ConvergentConnect(n, sd)
    Simulate(100.0)

import unittest
class TestModuleFunctions(unittest.TestCase):
    def setUp(self):
        from toolbox.network import default_params
        from toolbox import data_to_disk
        
        self.path=default_params.HOME+'/results/unittest/my_nest/'
        self.path_nest=self.path+'nest/'
        data_to_disk.mkdir(self.path_nest)
        
        ResetKernel()
        
    def clear(self,path):

        for _file in os.listdir(path):
            os.remove(path+_file)

    def get_nest_files(self):
        fn=[]
        for _file in os.listdir(self.path_nest):
            fn.append(self.path_nest+_file)
        return fn
  
  
    def test_delete_data(self):

        self.clear(self.path_nest)
        for i in range(4):
            fn=self.path_nest+'spk{}.gdf'.format(i)
            f=open(fn, 'wb')
            f.write('1')
            f.close()
            
        self.assertTrue(self.get_nest_files())
        delete_data(self.path_nest, **{'display':False})
        self.assertFalse(self.get_nest_files())

    def test_delete_data_mpi(self):

        import subprocess

        self.clear(self.path_nest)
        for i in range(4):
            fn=self.path_nest+'spk{}.gdf'.format(i)
            f=open(fn, 'wb')
            f.write('1')
            f.close()
                
        script_name=os.getcwd()+'/test_scripts_MPI/my_nest_delete_data_mpi.py'

        np=4
        
        p = subprocess.Popen(['mpirun',  '-np', str(np), 'python', 
                              script_name, self.path_nest, str(np)], 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
#             stderr=subprocess.STDOUT
            )
        out, err = p.communicate()
    #         print out
    #         print err
        
    def test_get_spikes_from_file(self):
        
        self.clear(self.path_nest)
        sim_group(self.path_nest)

        fn=self.get_nest_files()
        self.assertTrue(get_spikes_from_file(fn)[0].shape==(184,))

    def test_get_spikes_from_file_mpi(self):
        import subprocess
        
        self.clear(self.path_nest)
              
        script_name=os.getcwd()+'/test_scripts_MPI/my_nest_get_spikes_from_file_mpi.py'

        np=4
        
        p = subprocess.Popen(['mpirun',  '-np', str(np), 'python', 
                              script_name, self.path_nest, str(np)], 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
#             stderr=subprocess.STDOUT
            )
        out, err = p.communicate()
    #         print out
    #         print err

        fn=self.get_nest_files()
        self.assertTrue(get_spikes_from_file(fn)[0].shape==(184,))

    def test_Connect_DC(self):
        n=nest.Create('iaf_neuron', 10)
        model='static_synapse'
        delays=numpy.random.random(10)+2
        weights=numpy.random.random(10)+1
        
        post=[]
        for _id in n:
            post+=[_id]*10 
        
        Connect_DC(n*10,post,weights,delays,  model)
 
 
    def test_Connect_DC_mpi(self):
        import subprocess        
        self.clear(self.path_nest)

        script_name=os.getcwd()+'/test_scripts_MPI/my_nest_Connect_DC_mpi.py'
        data_out=self.path+'Connect_DC_mpi/'
        np=4
        
        p = subprocess.Popen(['mpirun',  '-np', str(np), 'python', 
                              script_name, data_out], 
#                                 stdout=subprocess.PIPE,
#                                 stderr=subprocess.PIPE,
            stderr=subprocess.STDOUT
            )
        out, err = p.communicate()
    #         print out
    #         print err
               
    
    
if __name__ == '__main__':
    d={
        TestModuleFunctions:[
                            'test_Connect_DC',
#                             'test_Connect_DC_mpi',
#                             'test_delete_data',
#                             'test_delete_data_mpi',
#                             'test_get_spikes_from_file',
#                             'test_get_spikes_from_file_mpi',
                             ],

       }
    test_classes_to_run=d
    suite = unittest.TestSuite()
    for test_class, val in  test_classes_to_run.items():
        for test in val:
            suite.addTest(test_class(test))

    unittest.TextTestRunner(verbosity=2).run(suite)
