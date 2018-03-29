%% Analysis of spiking data

% The purpose of this file is to plot all average firing rates in a
% colorplot for different amplitude of stimulation for each nucleus.

% function [] = main_all_avgfrs_multistim_avgdiff_fast(data_dir,data_dir_compare,...
%     res_dir,trial)
numtrs = 100;
global_counter = 0;                                        
spktimes = [];
spktimes_c = [];
spkids = [];
params = [];

DATA_DIR = '/space2/mohaghegh-data/temp-storage/17-12-15/mutlistim-STN-dur10.0-1000.0-2000.0-50.0';
DATA_DIR_C = '/space2/mohaghegh-data/temp-storage/17-12-15/STR-dur140.0-400.0-2000.0-100.0';
res_dir = '/space2/mohaghegh-data/temp-storage/17-12-15/';

fig_dir = [res_dir,'/figstemp/'];
if exist(fig_dir,'dir') ~= 7
    mkdir(fig_dir)
end

nuclei = {'FS','GA','GI','M1','M2','SN','ST'};
nc_names = {'FSI','GPe Arky','GPe Proto',...
            'MSN D1','MSN D2','SNr','STN'};
    
for tr_ind = 1:numtrs
    
%     if isempty(data_dir) && isempty(data_dir_compare)
%         data_dir = [pwd,'/STN-dur10.0-1000.0-2000.0-50.0/'];%mat_data/'];
%         data_dir_compare = [pwd,'/Ramp-dur140-amp200-1000-10/'];
%     end

    data_dir = [DATA_DIR,'-tr',num2str(tr_ind),'/'];
    data_dir_compare = [DATA_DIR_C,'-tr',num2str(tr_ind),'/'];

    stimvars = load([data_dir,'stimspec.mat']);
    stimvars_c = load([data_dir_compare,'stimspec.mat']);
    stimtimes_c = stimvars_c.STRramp.start_times + 150;    % The difference between
                                                    % start and stop times.
    stimrate_c = stimvars_c.STRramp.rates;               % Rate in ramp sim.
    
    stim_targets = fieldnames(stimvars);
    stimvars_cell = struct2cell(stimvars);
    for nc_ind = 1:length(stimvars_cell)
        if length(stim_targets{nc_ind}) <= 2
            stim_pop(nc_ind).allpop = stimvars_cell{nc_ind}.allpop;
            stim_pop(nc_ind).subpop = stimvars_cell{nc_ind}.stim_subpop;
        %     stim_vecs(nc_ind).STN   = stimvars_cell{nc_ind}.STNstop;
        %     stim_vecs(nc_ind).STR   = stimvars_cell{nc_ind}.STRramp;
            switch stim_targets{nc_ind}
                case 'CS'
                    stim_targets{nc_ind} = 'ST';
                case 'C1'
                    stim_targets{nc_ind} = 'M1';
                case 'C2'
                    stim_targets{nc_ind} = 'M2';
                case 'CF'
                    stim_targets{nc_ind} = 'FS';
            end
        else
            switch stim_targets{nc_ind}
                case 'STRramp'
                    stimtimes = stimvars_cell{nc_ind}.stop_times;
                    stimrate = stimvars_cell{nc_ind}.rates;
            end
        end
    end
    % stimtimes = stim_vecs(1).STN.stop_times;
    % stimrate = stim_vecs(1).STN.rates;
    str_f = unique(stimrate(1,:));      % Max cortical rate to STR
    stn_f = unique(stimrate(2,:));      % Max cortical rate to STN
%    stn_f = stn_f([5,10,end]);
    str_stn_lat = unique(stimrate(3,:));% Time interval between STR and STN

    % Averaging window 

    win_width = 50;
    overlap = 10;

    % nuclei_fr_hist(nuclei)
    
    all_diff_struc = struct([]);

    for nc_id = 6:6%length(nuclei)
        
        diff_struc = struct([]);
        
        %% Data of ramping and stop-signal
        
        data = load([data_dir,'mat_data/',nuclei{nc_id},'-spikedata']);
        IDsall = double(data.N_ids);
        IDs = IDsall - min(IDsall) + 1;
        spk_times = double(data.spk_times)/10;
    %     spk_times_d = double(spk_times);
        numunits = max(IDs) - min(IDs) + 1;
        
        %% Data of stop signal
        
        data_c = load([data_dir_compare,'mat_data/',nuclei{nc_id},'-spikedata']);
%         IDsall = double(data_c.N_ids);
%         IDs = IDsall - min(IDsall) + 1;
        spk_times_c = double(data_c.spk_times)/10;
    %     spk_times_d = double(spk_times);
%         numunits = max(IDs) - min(IDs) + 1;
%         numunits = max(IDs) - min(IDs) + 1;

%         if sum(strcmpi(nuclei{nc_id},stim_targets)) > 0
%             sel_tar = strcmpi(nuclei{nc_id},stim_targets);
%             tar_ids = stim_pop(sel_tar).allpop;
%             tar_stim_ids = stim_pop(sel_tar).subpop;
%             tar_stim_ids = tar_stim_ids - min(tar_ids) + 1;
%             [subpop_ids,subpop_spktimes] = ...
%             spk_id_time_subpop_ex(tar_stim_ids,IDs,spk_times);
%         end

    %     if strcmpi(nuclei{nc_id},'SN')
    %         silent_snr_id(IDs,spk_times,fig_dir)
    %     end
        for stnf_ind = 1:length(stn_f)
            disp(['Stim STN = ',num2str(stn_f(stnf_ind))])
            for rel_time_ind = 1:length(str_stn_lat)
                disp(['Rel time = ',num2str(str_stn_lat(rel_time_ind))])
                sel_stimtimes = stimtimes(...
                                stimrate(3,:) == str_stn_lat(rel_time_ind) & ...
                                stimrate(2,:) == stn_f(stnf_ind));

                for st_id = 1:length(sel_stimtimes)
                    global_counter = global_counter + 1;
                    str_freq = stimrate(1,stimtimes == sel_stimtimes(st_id));
                    disp([nuclei{nc_id},'-',num2str(st_id)])
                    st_time = sel_stimtimes(st_id) - 500;
                    end_time = sel_stimtimes(st_id) + 500;
%                     [cnt(st_id,:),cnttimes] = PSTH_mov_win(spk_times,win_width,overlap,st_time,end_time,numunits,1);
                    temp_spks = spk_times(spk_times>=st_time & ...
                                                   spk_times<=end_time);
                    spktimes = [spktimes;[temp_spks,global_counter * ones(size(temp_spks))]];
                    params = [params,[nc_id;stn_f(stnf_ind);...
                                      str_stn_lat(rel_time_ind);str_freq;...
                                      global_counter;tr_ind;...
                                      numunits]];
                    
                    
                    sel_stimtimes_c = stimtimes_c(stimrate_c == str_freq);
                    st_time = sel_stimtimes_c - 500;
                    end_time = sel_stimtimes_c + 500;
%                     [cnt_str(st_id,:),cnttimes_str] = PSTH_mov_win(spk_times_c,win_width,overlap,st_time,end_time,numunits,1);
                    
                    temp_spks = spk_times(spk_times>=st_time & ...
                               spk_times<=end_time);
                    spktimes_c = [spktimes_c;[temp_spks,global_counter * ones(size(temp_spks))]];
                end
            end
                
        end

    end
end

params = [params,[nc_id;stn_f(stnf_ind);...
                                      str_stn_lat(rel_time_ind);str_freq;...
                                      tr_ind;...
                                      numunits;global_counter]];
                                  
params_cat = {'nuclei','STN_freq','Latency','STR_freq','Trial','num_units','Counter'};

save([fig_dir,'diffmat-tr',num2str(trial)],'spktimes','spktimes_c',...
                                            'params','params_cat','nuclei',...
                                            'nc_names','DATA_DIR',...
                                            'DATA_DIR_C','res_dir')

% function [ids,spktimes] = spk_id_time_ex(dir)
%     data = load(dir);
%     IDs = double(data.N_ids);
%     ids = IDs - min(IDs);
%     spktimes = double(data.spk_times)/10;
% %     spk_times_d = double(spk_times);
% %    numunits = max(ids) - min(ids) + 1;
% end
% function [stim_ids,stim_spktimes] = spk_id_time_subpop_ex(subpop_ids,ids,spk_times)
%     stim_ids = [];
%     stim_spktimes = [];
%     for sp_ind = 1:length(subpop_ids)
%         stim_ids = [stim_ids;ids(ids == subpop_ids(sp_ind))];
%         stim_spktimes = [stim_spktimes;spk_times(ids == subpop_ids(sp_ind))];
%     end
% end
% function renumbered = ids_renum_for_raster(IDs)
%     IDs_u = unique(IDs);
%     renumbered = IDs;
%     for ind = 1:length(IDs_u)
%         renumbered(renumbered == IDs_u(ind)) = ind;
%     end
% end
% function [] = silent_snr_id(ids,spk_times,fig_dir)
%     ids_u = unique(ids);
%     for id_ind = 1:length(ids_u)
%         spks_in_id = sort(spk_times(ids==ids_u(id_ind)));
%         figure;
%         histogram(diff(spks_in_id),[0:10:100])
%         GCA = gca;
%         GCA.FontSize = 14;
%         xlabel('ISI (ms)')
%         ylabel('Counts')
%         title(['SNr unit # ',num2str(ids_u(id_ind))])
%         histdir = [fig_dir,'ISIhist/'];
%         if exist(histdir,'dir') ~= 7
%             mkdir(histdir)
%         end
%         fig_print(gcf,[histdir,'ISIhist-SNr-',num2str(ids_u(id_ind))])
%         close(gcf)
%     end
% end
% function [] = nuclei_fr_hist(nuclei,fig_dir)
%     for nc_id = 1:length(nuclei)
%         [IDs,spk_times] = spk_id_time_ex([data_dir,'mat_data/',nuclei{nc_id},'-spikedata']);
%         IDs_u = unique(IDs);
%         firingrates = zeros(2,length(IDs_u));
% 
%         for id_ind = 1:length(IDs_u)
%             firingrates(1,id_ind) = IDs(id_ind);
%             firingrates(2,id_ind) = sum(IDs == IDs_u(id_ind))/max(spk_times)*1000;
%         end
% 
%         SUFR(nc_id).nc_name = nuclei(nc_id);
%         SUFR(nc_id).fr_ids = firingrates;
%         figure;
%         histogram(firingrates(2,:),20)
%         GCA = gca;
%         GCA.FontSize = 14;
%         GCA.Box = 'off';
%         GCA.TickDir = 'out';
%         histdir = [fig_dir,'ISIhist/'];
%         fig_print(gcf,[histdir,'hist-',nuclei{nc_id}])
%         close(gcf)  
%     end
% end
