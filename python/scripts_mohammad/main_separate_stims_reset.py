# Create by Mikael Lindahl on 4/12/17.

from core.network import structure
from core.network import engine
from core import my_nest, data_to_disk
# from core.network.parameters.eneuro import EneuroPar
from core.network.parameters.eneuro_NoDynSyn import EneuroPar as Eneuropar_NDS
from core.network.parameters.eneuro import EneuroPar

# from core.network.parameters.eneuro_activation_NoDynSyn import EneuroActivationPar
from core.network.parameters.eneuro_activation import EneuroActivationPar
from core.network.parameters.eneuro_activation_beta import EneuroActivationBetaPar
from core.network.parameters.eneuro_sw import EneuroSwPar

from core.network.parameters.eneuro_ramp import EneuroRampPar
# from core.network.default_params import Beta
from scripts_inhibition.base_oscillation import add_GI, add_GPe
import pprint
import json
import os
import sys

import plot
import randomized_params_plot
import mean_firing_rates
import mean_firing_rates_plot
import list_parameters

import scipy.io as sio
import numpy
import nest
import time

pp = pprint.pprint


def save_node_random_params(pops, path):

    d = {}

    for node in ['FS', 'GI',  'GF', 'GA', 'M1', 'M2', 'ST', 'SN']:

        d[node] = {}

        for param in ['V_th', 'V_m', 'C_m', 'E_L']:

            d[node][param] = [s[param] for s in my_nest.GetStatus(pops[node].ids)]


        d[node]['V_th-E_L']= [a-b for a,b in zip(d[node]['V_th'], d[node]['E_L'])]


    if not os.path.isdir(os.path.dirname(path)):
        data_to_disk.mkdir(os.path.dirname(path))

    json.dump( d, open(path, 'w'))

def build(par):
    # ******
    # Build
    # ******
    surfs, pops = structure.build(par.get_nest(),
                                  par.get_surf(),
                                  par.get_popu())

    return surfs, pops


def connect(par, surfs, pops):
    args = [pops, surfs, par.get_nest(), par.get_conn(), True]

    structure.connect(*args)


def postprocessing(pops):
    d = {}

    signal_type = 'spike_signal'

    d_signals = pops.get(signal_type)

    for name, signal in d_signals.items():
        engine.fill_duds_node(d, name, signal_type, signal)

    add_GI(d)
    add_GPe(d)

    return d


# def main(mode, size, trnum, threads_num, les_src,les_trg,chg_gpastr,total_num_trs,stat_syn):
def main(mode, size, trnum, threads_num, les_src,les_trg,stim_pars,stim_chg_pars, tmpdir, chg_gpastr, w_gpastr, total_num_trs, stat_syn):
    my_nest.ResetKernel()

    # Get parameters
    # par = EneuroBetaPar(other=EneuroPar())

    if mode in ['activation-control',  'activation-dopamine-depleted']:

        if mode == 'activation-control':
            if stat_syn:
                par = EneuroActivationPar(other=Eneuropar_NDS())
                print 'All synapses are static!'
            else:
                par = EneuroActivationPar(other=EneuroPar())
                print 'Default synaptic configuration!'
            dop = 0.8

        elif mode == 'activation-dopamine-depleted':
            par = EneuroActivationBetaPar(other=EneuroPar())
            dop = 0.0

    elif mode in ['slow-wave-control', 'slow-wave-dopamine-depleted']:

        par = EneuroSwPar(other=EneuroPar())

        if mode == 'slow-wave-control':
            dop = 0.8
        elif mode == 'slow-wave-dopamine-depleted':
            dop = 0.0


    pp(stim_pars)
    pp(stim_chg_pars)

    # Changing GPA to STR connection weight leading to prominent response in STR

    binalg = False

    if chg_gpastr:
        # div_var = trnum/total_num_trs
        # trnum = ((trnum-1)%total_num_trs) + 1
        # if binalg:
        #     weight_coef_base = 0.5
        #
        #     # residual_temp = div_var%2
        #     if (div_var%2) == 0:
        #         weight_coef = weight_coef_base + weight_coef_base/(2**(div_var/2))
        #     else:
        #         weight_coef = weight_coef_base - weight_coef_base/(2**(div_var+1)/2)
        # else:
        #     weight_coef_base = 0.2
        #     weight_coef_inc_rate = 0.05
        #
        #     weight_coef = weight_coef_base + weight_coef_inc_rate * div_var

        weight_coef = w_gpastr

        par.set({'nest':{'GA_M1_gaba':{'weight':weight_coef}}})
        par.set({'nest':{'GA_M2_gaba':{'weight':weight_coef*2.0}}})
    else:
        weight_coef = par.dic['nest']['GA_M1_gaba']['weight']
        div_var = 0


    '''
        The naming of the result directory has the following order:
        1st number: stimulation duration
        2nd number: maximum rate increase
        3rd number: maximum change of rate increase
        4th number: steps of increase
    '''

    # dir_name = 'GPASTR-Wmod'+str(int(weight_coef*100))+'-' + str(div_var) + '-'
    dir_name = 'GPASTR-Wmod'+str(int(weight_coef*100))+'-'

    for keys in stim_pars:
        if stim_pars[keys]['do']:
            dir_name = dir_name + \
                       stim_pars[keys]['target_name']+'-'+\
                       str(int(stim_pars[keys]['h_rate']))+ '-'+\
                       str(int(stim_chg_pars[keys]['value']))
            if keys in stim_chg_pars['Reltime']:
                dir_name += '-'+ str(int(stim_chg_pars['Reltime'][keys]['h_val']))
            last_stimpars = keys

    if stat_syn:
        dir_name = dir_name + '-static-'
    else:
        dir_name = dir_name + '-tsodyks-'

    dir_name = dir_name + 'tr'+ str(trnum)

    base = os.path.join(os.getenv('BGMODEL_HOME_DATA'), 'example/eneuro', str(size), mode, dir_name)



    rand_conn = False

    if rand_conn:
        pathconn = par.get()['simu']['path_conn']+ str(trnum)+ '/'
    else:
        pathconn = par.get()['simu']['path_conn']
        #Setting python random number generator
        rng_py = numpy.random.RandomState(seed=1000)

    if len(les_src) > 0:
        print 'Lesion will be applied to source(s): ',les_src,' projecting to ',les_trg
        lesion(par,les_src,les_trg)
    else:
        print 'No lesion!'

    if tmpdir:
        base = os.path.join(os.getenv('TMPDIR'), 'example/eneuro', str(size), mode, dir_name)



    # Configure simulation parameters
    par.set({
        'simu': {
            'local_num_threads': threads_num,
            'path_data': base+'/data',
            'path_figure': base+'/fig',
            'path_nest': base+'/nest/',  # trailing slash important
            'path_conn': pathconn,
            'stop_rec': 10000000.,
            'sim_stop': 10000000.,
            'print_time': True,
            'sd_params': {
                'to_file': True,
                'to_memory': False
            },

        },
        'netw': {
            'tata_dop':dop,
            'size': size
        },
        # 'node': {
        #     'C1': {'rate': 546.},
        #     'C2': {'rate': 722.},
        #     'CF': {'rate': 787.},
        #     'CS': {'rate': 250.},
        #     'ES': {'rate': 1530.}
        # },
        # 'conn':{'GA_M1_gaba':{'weight':{'params':{'max':1.0,'min':0.6}}},   # Default: min = 0.02; max = 0.06
        #         'GA_M2_gaba':{'weight':{'params':{'max':2.0,'min':1.2}}}}, # Default: min = 0.04; max = 0.12
    })

    mod_GPASTR_weights = {'GA_M1':par.dic['conn']['GA_M1_gaba']['weight']['params'],
                          'GA_M2':par.dic['conn']['GA_M2_gaba']['weight']['params']}

    par.nest_set_kernel_status()

    # Save parametesr
    list_parameters.main(base, par)

    # Clear nest data directory
    par.nest_clear_data_path({'display': True})

    # Show kernel status
    pp(my_nest.GetKernelStatus())

    sim_res = nest.GetKernelStatus('resolution')

    #Setting nest random number generator
    nest_rng_set(trnum)


    # Create news populations and connections structures
    surfs, pops = build(par)

    #Example getting C1 nest ids
    # >> pops['C1'].ids
    # Extracting nodes which are going to get the modulatory input
    # STR
    stim_combine = []
    for key in stim_pars.keys():
        stim_combine.append(stim_pars[key]['do'])

    ind_comb = -1
    comb_dic = {}

    if sum(stim_combine) == len(stim_combine):
    # if sum(stim_combine) > 1:
        ratescomb = []
        for stim_type in stim_pars.keys():
            ind_comb = ind_comb + 1
            # l_rate = stim_pars[stim_type]['l_rate']
            h_rate = stim_pars[stim_type]['h_rate']
            ratescomb.append(numpy.array(h_rate))
            comb_dic.update({stim_type:ind_comb})
        reltimecomb = []
        if stim_chg_pars.has_key('Reltime'):
            for rel_type in stim_chg_pars['Reltime'].keys():
                ind_comb = ind_comb + 1
                # h_value = stim_chg_pars['Reltime'][rel_type]['h_val']
                l_value = stim_chg_pars['Reltime'][rel_type]['h_val']
                # res_val = stim_chg_pars['Reltime'][rel_type]['res']
                reltimecomb.append(numpy.array(l_value))
                if comb_dic.has_key('reltime'):
                    comb_dic['reltime'].update({rel_type:ind_comb})
                else:
                    comb_dic.update({'reltime':{rel_type:ind_comb}})
            # comb = numpy.array(numpy.meshgrid(ratescomb[0],ratescomb[1],ratescomb[2],reltimecomb[0],reltimecomb[1]))
            comb = numpy.append(ratescomb, reltimecomb)
        # comb_resh = comb.reshape(comb.shape[0],numpy.prod(comb.shape[1:]))
        comb_resh = comb
        stim_time = modulatory_multiplestim(comb_resh,stim_pars,stim_chg_pars,comb_dic,tot_num_trs)
        stim_spec = {'C1':0.0,'C2':0.0,'CF':0.0,'CS':0.0,'EA':0.0}
        for stim_type in stim_time.keys():
            for node_name in stim_pars[stim_type]['stim_target']:
                [modpop_ids,allpop_ids] = extra_modulation(pops, stim_pars[stim_type]['stim_ratio'][node_name], node_name, rng_py)
                nest.Connect(stim_time[stim_type]['stim_pois_id'], modpop_ids)
                # stim_spec[node_name] = stim_time
                stim_spec[node_name] = {'stim_subpop':modpop_ids,
                                        'allpop':allpop_ids,
                                        'stim_id':stim_time[stim_type]['stim_pois_id']}
        stim_spec.update(stim_time)

    elif sum(stim_combine) > 1 and sum(stim_combine) != len(stim_combine):
        ratescomb = []
        for stim_type in stim_pars.keys():
            if stim_pars[stim_type]['do']:
                ind_comb = ind_comb + 1
                # l_rate = stim_pars[stim_type]['l_rate']
                h_rate = stim_pars[stim_type]['h_rate']
                # res = stim_chg_pars[stim_type]['res']
                # max_h_rate = stim_chg_pars[stim_type]['value']
                ratescomb.append(numpy.array(h_rate))
                comb_dic.update({stim_type:ind_comb})
            else:
                stim_pars.pop(stim_type)
                stim_chg_pars.pop(stim_type)
                stim_chg_pars['Reltime'].pop(stim_type)
        reltimecomb = []
        if stim_chg_pars.has_key('Reltime'):
            for rel_type in stim_chg_pars['Reltime'].keys():
                if stim_pars[rel_type]['do']:
                    ind_comb = ind_comb + 1
                    # h_value = stim_chg_pars['Reltime'][rel_type]['h_val']
                    l_value = stim_chg_pars['Reltime'][rel_type]['h_val']
                    # res_val = stim_chg_pars['Reltime'][rel_type]['res']
                    reltimecomb.append(numpy.array(l_value))
                    if comb_dic.has_key('reltime'):
                        comb_dic['reltime'].update({rel_type:ind_comb})
                    else:
                        comb_dic.update({'reltime':{rel_type:ind_comb}})
            # comb = numpy.array(numpy.meshgrid(ratescomb[0],ratescomb[1],reltimecomb[0]))
        # comb_resh = comb.reshape(comb.shape[0],numpy.prod(comb.shape[1:]))
        comb = numpy.append(ratescomb, reltimecomb)
        comb_resh = comb
        stim_time = modulatory_multiplestim(comb_resh,stim_pars,stim_chg_pars,comb_dic,tot_num_trs)
        stim_spec = {'C1':0.0,'C2':0.0,'CF':0.0,'CS':0.0}
        for stim_type in stim_time.keys():
            for node_name in stim_pars[stim_type]['stim_target']:
                [modpop_ids,allpop_ids] = extra_modulation(pops, stim_pars[stim_type]['stim_ratio'][node_name], node_name, rng_py)
                nest.Connect(stim_time[stim_type]['stim_pois_id'], modpop_ids)
                # stim_spec[node_name] = stim_time
                stim_spec[node_name] = {'stim_subpop':modpop_ids,
                                        'allpop':allpop_ids,
                                        'stim_id':stim_time[stim_type]['stim_pois_id']}
        stim_spec.update(stim_time)

    else:
        dic_keys = numpy.array(stim_pars.keys())
        whichkey = dic_keys[numpy.array(stim_combine)][0]
        stim_spec = stim_pars[whichkey]['stim_spec']
        for node_name in stim_pars[whichkey]['stim_target']:
            [modpop_ids,allpop_ids] = extra_modulation(pops, stim_pars[whichkey]['stim_ratio'][node_name], node_name, rng_py)
            [stimmod_id,stim_time] = modulatory_stim(stim_pars[whichkey],stim_chg_pars[whichkey])
            nest.Connect(stimmod_id,modpop_ids)
            # stim_spec[node_name] = stim_time
            stim_spec[node_name] = {'stim_subpop':modpop_ids,
                                    'allpop':allpop_ids,
                                    'stim_id':stimmod_id}
        stim_spec.update({whichkey:stim_time})

    sio.savemat(base+'/stimspec.mat',stim_spec)
    sio.savemat(base+'/modifiedweights.mat',mod_GPASTR_weights)

    save_node_random_params(pops,base+'/randomized-params.json')
    nest.SetKernelStatus({'print_time':True})

    # print(pops)

    # Connect populations accordingly to connections structure
    connect(par, surfs, pops)

    # Initializing path container list
    gdfdatadirs = []

    #
    # # Simulate
    print 'Simulation\'s just started ...'
    if sum(stim_combine) > 0:
        # my_nest.Simulate(max(stim_spec[last_stimpars]['start_times'])+5000.0)
        nest.SetKernelStatus({'overwrite_files':True})
        resettimes = stim_spec['STRramp']['reset_times']
        simtime = numpy.unique(numpy.diff(resettimes))[0]
        for tr in range(tot_num_trs):
            print 'Simulation trial #', str(tr+1)
            my_nest.Simulate(simtime)
            nest.ResetNetwork()
            rep_dir = os.path.join(base, str(tr+1))
            gdfdatadirs.append(rep_dir)
            ensure_dir(rep_dir)
            print 'Moving gdf files to ', rep_dir, '...'
            os.system('cp -r '+base+'/nest '+rep_dir+'/')
            time.sleep(10.0)
    else:
        my_nest.Simulate(10000.0)

    print 'Simulation is now finished!\n'

    return gdfdatadirs

def extra_modulation(pops,subpop_ratio,node_name,rand_gen):
    node_ids = pops[node_name].ids
    perm_ids = rand_gen.permutation(node_ids)
    #subpop_ratio = 0.3
    subpop_num = numpy.int(subpop_ratio*len(node_ids))
    subpop_ids = perm_ids[range(0,subpop_num)]
    subpop_ids = subpop_ids.tolist()
    return subpop_ids,node_ids

def modulatory_stim(stim_params,chg_stim_param):
    mod_inp = nest.Create('poisson_generator_dynamic',1)
    all_rates = []
    all_start_times = []
    stim_start = stim_params['stim_start']
    h_rate = stim_params['h_rate']
    l_rate = stim_params['l_rate']
    #slope = stim_params['slope']
    stim_dur = stim_params['duration']
    res = stim_params['res']
    # rate_step = slope*res
    stim_stop = stim_start + stim_dur + res
    timevec = numpy.arange(stim_start,stim_stop,res)
    timveclen = timevec.size
    ratevec = numpy.linspace(l_rate,h_rate,timveclen)

    chg_stim_val = chg_stim_param['value']
    chg_stim_res = chg_stim_param['res']
    waittime = chg_stim_param['waittime']
    all_start_times.append(stim_start)
    all_rates.append(h_rate)
    h_rate = h_rate + chg_stim_res

    while h_rate <= chg_stim_val:
        all_rates.append(h_rate)
        ratevec = numpy.append(ratevec,0.0)
        timevec = numpy.append(timevec,timevec[-1]+res)

        if stim_params['w-form'] == 'ramp':
            ratevec = numpy.append(ratevec,numpy.linspace(l_rate,h_rate,timveclen))
        elif stim_params['w-form'] == 'pulse':
            ratevec_tmp = []
            ratevec_tmp.append(l_rate)
            ratevec_tmp = numpy.append(ratevec_tmp,h_rate*numpy.ones(timveclen - 1))
            ratevec = numpy.append(ratevec,ratevec_tmp)

        stim_start = stim_stop + waittime
        stim_stop = stim_start + stim_dur + res
        timevec = numpy.append(timevec,numpy.arange(stim_start,stim_stop,res))
        h_rate = h_rate + chg_stim_res
        all_start_times.append(stim_start)

    nest.SetStatus(mod_inp,{'rates': ratevec.round(0),'timings': timevec,
                            'start': timevec[0], 'stop': stim_stop})
    stim_vecs = {'rates':all_rates,
                 'start_times':all_start_times}
    return mod_inp,stim_vecs

def modulatory_multiplestim(all_rates,stim_params,chg_stim_param,comb_dic,tot_numtr):
    num_pois_gen = len(stim_params.keys())
    mod_inp = nest.Create('poisson_generator_dynamic',num_pois_gen)
    ind = -1
    ind_dic = {}
    stim_vecs = {}
    refchgkey = list(find('ref',chg_stim_param))
    u_refchgkey = numpy.unique(refchgkey)[0]
    if type(u_refchgkey) is not list:
        ordered_keys = [u_refchgkey]
    for keys in stim_params.keys():
        ind = ind + 1
        ind_dic.update({keys:ind})
        if not keys in u_refchgkey:
            ordered_keys.append(keys)


    for keys in ordered_keys:
        ind = ind_dic[keys]
        timevec = numpy.array(0.0)
        ratevec = numpy.array(0.0)
        waittime = chg_stim_param[keys]['waittime']
        dead_time = chg_stim_param[keys]['deadtime']
        prep_time = chg_stim_param[keys]['preptime']
        # stim_start = stim_params[keys]['stim_start']
        stim_start = dead_time + prep_time
        # all_rates = []
        all_start_times = []
        all_stop_times = []
        all_reset_times = []
        # for rate_ind, rateval in enumerate(all_rates[ind]):
        for dum in range(tot_numtr):
            rate_ind = 0
            rateval = all_rates[ind]
            h_rate = rateval
            l_rate = stim_params[keys]['l_rate']
            #slope = stim_params['slope']
            stim_dur = stim_params[keys]['duration']
            res = stim_params[keys]['res']
            # rate_step = slope*res
            if keys in refchgkey:
                stim_stop = stim_start + stim_dur + res
            else:
                # stim_start = prev_var_stops[rate_ind] + all_rates[comb_dic['reltime'][keys]][rate_ind]
                stim_start = prev_var_stops[dum] + all_rates[comb_dic['reltime'][keys]]
                stim_stop = stim_start + stim_dur + res
            single_timvec = numpy.arange(stim_start,stim_stop,res)
            timevec = numpy.append(timevec,single_timvec)
            timveclen = single_timvec.size
            # ratevec = numpy.append(ratevec,numpy.linspace(l_rate,h_rate,timveclen))

            if stim_params[keys]['w-form'] == 'ramp':
                ratevec = numpy.append(ratevec,numpy.linspace(l_rate,h_rate,timveclen))
            elif stim_params[keys]['w-form'] == 'pulse':
                ratevec_tmp = []
                ratevec_tmp.append(l_rate)
                ratevec_tmp = numpy.append(ratevec_tmp,h_rate*numpy.ones(timveclen - 1))
                ratevec = numpy.append(ratevec,ratevec_tmp)

            # Establishing the pause between the stimulations
            ratevec = numpy.append(ratevec,0.0)
            timevec = numpy.append(timevec,timevec[-1]+res)

            reset_times = stim_start + waittime

            all_start_times.append(stim_start)
            all_stop_times.append(stim_stop)
            all_reset_times.append(reset_times)

            stim_start = stim_start + waittime + dead_time + prep_time

        if keys in refchgkey:
            prev_var_stops = all_stop_times

        nest.SetStatus((mod_inp[ind],),{'rates': ratevec.round(0),'timings': timevec,
                                'start': timevec[0], 'stop': stim_stop})
        stim_vecs.update({keys:{'rates':all_rates,
                                'start_times':all_start_times,
                                'stop_times':all_stop_times,
                                'reset_times':all_reset_times,
                                'stim_pois_id':(mod_inp[ind],)}})
    return stim_vecs

def lesion(params,source,target):
    connlist = params.get()['conn']
    connkeys = connlist.keys()
    for keys in connkeys:
        str_temp = keys.split('_')
        if str_temp[0] in source and str_temp[1] in target:
            params.set({'conn':{keys:{'lesion':True}}})
    return params

def find(key, dictionary):
    for k, v in dictionary.iteritems():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result

def nest_rng_set(tr):
    def_rng_seed = nest.GetKernelStatus('rng_seeds')
    l_def_rng_seed = len(def_rng_seed)
    l_lim = (tr - 1)*l_def_rng_seed + 1
    u_lim = l_lim + l_def_rng_seed
    nest.SetKernelStatus({'rng_seeds':range(l_lim,u_lim,1)})

def ensure_dir(directory):
    # directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

# main()
if __name__ == '__main__':

    dir_list = []
    sim_res = 0.1

    stim_pars = {'STRramp':{'stim_start':4000.0,
                             'h_rate':400.0,
                             'l_rate':350.0,
                             'duration':140.0,
                             'res':10.0,
                             'do':True,
                             'w-form':'ramp',
                             'stim_target':['C1','C2','CF'],
                             'target_name':'STR',
                             'stim_spec':{'C1':0.0,'C2':0.0,'CF':0.0},
                             'stim_ratio':{'C1':0.3,'C2':0.3,'CF':0.3}},
                 'STNstop':{'stim_start':4000.0,
                             'h_rate':1000.0,
                             'l_rate':0.0,
                             'duration':10.0,
                             'res':2.0,
                             'do':True,
                             'w-form':'pulse',
                             'stim_target':['CS'],
                             'target_name':'STN',
                             'stim_spec':{'CS':0.0},
                             'stim_ratio':{'CS':1.0}},
                 'GPAstop':{'stim_start':4000.0,
                             'h_rate':1000.0,
                             'l_rate':0.0,
                             'duration':40.0,
                             'res':2.0,
                             'do':True,
                             'w-form':'pulse',
                             'stim_target':['EA'],
                             'target_name':'GPA',
                             'stim_spec':{'EA':0.0},
                             'stim_ratio':{'EA':1.0}}}
    stim_chg_pars = {'STRramp':{'value':500.0,
                                'res':100.0,
                                'waittime':2000.0,
                                'deadtime':1000.0,
                                'preptime':2000.0},
                     'STNstop':{'value':2000.0,
                                'res':500.0,
                                'waittime':2000.0,
                                'deadtime':1000.0,
                                'preptime':2000.0},
                     'GPAstop':{'value':2000.0,
                                'res':500.0,
                                'waittime':2000.0,
                                'deadtime':1000.0,
                                'preptime':2000.0},
                     'Reltime':{'STNstop':{'l_val':0.0,
                                       'h_val':20.0,
                                       'res':10.0,
                                       'ref':'STRramp'},
                                'GPAstop':{'l_val':0.0,
                                       'h_val':20.0,
                                       'res':10.0,
                                       'ref':'STRramp'}}}

    str_f = numpy.arange(600.,1000.,100.)
    gpa_f = numpy.arange(500.,2000.,500.)
#     gpa_f = numpy.array([0.0])
    stn_f = numpy.arange(500.,2000.,500.)
    # stn_f = numpy.array([0.0])
    relss = numpy.arange(-120.,-50.,10.)
#    relss = numpy.array([-120.0])
    relsgss = 10.0
    relsgwid = 50.0
    relsgres = 10.0
    # relsg = numpy.arange(-100.,-80.,10.)
    # weivec = numpy.arange(0.2,0.7,0.1)

#     relsg = numpy.array([0.0])

    comb = numpy.array(numpy.meshgrid(str_f,stn_f,gpa_f,relss))
    comb_resh = comb.reshape(comb.shape[0],numpy.prod(comb.shape[1:]))

    if len(sys.argv) > 1:
        numtrs = int(sys.argv[1]) - 1
        size = int(sys.argv[2])
        loc_num_th = int(sys.argv[3])
        W_GPASTR = float(sys.argv[4])
        tot_num_trs = int(sys.argv[5])
    else:
        numtrs = 100
        size = 3000
        loc_num_th = 1
        lesion_source = []
        lesion_target = []
        chg_GPASTR = False
        W_GPASTR = 0.3
        tot_num_trs = 3

    if len(sys.argv) > 6:
        les_s_tmp = sys.argv[6]
        lesion_source = les_s_tmp.split(',')
        les_t_tmp = sys.argv[7]
        lesion_target = les_t_tmp.split(',')
    else:
        lesion_source = []
        lesion_target = []

    # if len(sys.argv) > 7:                       # GPA to STR connections get strengthen so that they can affect ramping
    #     tot_num_trs = int(sys.argv[7])          # response in MSN D1 and D2
    #     chg_GPASTR = True
    # else:
    #     # tot_num_trs = 100
    #     # chg_GPASTR = True
    tmpdir = True

    if not W_GPASTR:
        chg_GPASTR = False
    else:
        chg_GPASTR = True

    modes = ['activation-control']

    all_static_syns = False

#    modes = [
#        'activation-control',
#        'activation-dopamine-depleted',
#        'slow-wave-control',
#        'slow-wave-dopamine-depleted'
#    ]
    ind = numtrs
    STNreltime = comb_resh[3][ind]
    GPAreltime = numpy.arange(STNreltime+relsgss,STNreltime+relsgss+relsgwid,relsgres)
    for gprt in GPAreltime:

        stim_pars['STRramp']['h_rate'] = comb_resh[0][ind]
        stim_pars['STNstop']['h_rate'] = comb_resh[1][ind]
        stim_pars['GPAstop']['h_rate'] = comb_resh[2][ind]
        stim_chg_pars['Reltime']['STNstop']['h_val'] = comb_resh[3][ind]
        stim_chg_pars['Reltime']['GPAstop']['h_val'] = gprt

        print 'STR = ', str(int(comb_resh[0][ind])), ', STN = ', str(int(comb_resh[1][ind])),\
              ', GPA = ', str(int(comb_resh[2][ind])), ', RSS = ', str(int(comb_resh[3][ind])),\
              ', RSG = ', str(int(gprt))

        # for mode in modes:
        mode = modes[0]
        nest_data_dir = main(mode, size, numtrs, loc_num_th, lesion_source, lesion_target, stim_pars, stim_chg_pars, tmpdir,chg_GPASTR,W_GPASTR,tot_num_trs,all_static_syns)

        # print 'nest directory \"'+ nest_data_dir +'\" finished processing!'
        print 'Processing finished! data stored in '
        print nest_data_dir

        main_dir = nest_data_dir[0].rsplit('/',1)[0]
        weight_stim_dir = nest_data_dir[0].rsplit('/',1)[0]
        trialnum = int(nest_data_dir[0].rsplit('/',1)[1])
        main_dir_flname = main_dir + '/dir-data.mat'

        print 'directories path are stored in: '+ main_dir_flname

        sio.savemat(main_dir_flname,{'dirs':nest_data_dir,
                                     'wsdir':weight_stim_dir})

        os.system('matlab -nodisplay -r \'data_concat_save_as_mat_sep_stim_reset '+ main_dir_flname+ ' '+ str(sim_res)+ '; exit;\'')