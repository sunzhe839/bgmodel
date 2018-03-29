%% Analysis of spiking data

% The purpose of this file is to plot all average firing rates in a
% colorplot for different amplitude of stimulation for each nucleus.

function [] = main_all_avgfrs_GPA_stim()
data_dir = ['/space2/mohaghegh-data/Working-Directory/PhD/Projects/BGmodel/bgmodel/results/example/eneuro/10000/activation-control/GPA-40.0-500.0-5000.0-500.0-tr1/'];%mat_data/'];
fig_dir = [data_dir,'/figs/'];
if exist(fig_dir,'dir') ~= 7
    mkdir(fig_dir)
end
nuclei = {'FS','GA','GI','M1','M2','SN','ST'};
nc_names = {'FSI','GPe Arky','GPe Proto',...
            'MSN D1','MSN D2','SNr','STN'};

stimvars = load([data_dir,'stimspec.mat']);
stimtimes = stimvars.GPAstop.start_times;
stimrate = stimvars.GPAstop.rates;
STids = stimvars.EA.stim_subpop;
STall = stimvars.EA.allpop;
% M2ids = stimvars.C2.stim_subpop;
% M2all = stimvars.C2.allpop;
% FSids = stimvars.CF.stim_subpop;
% FSall = stimvars.CF.allpop;

% Averaging window 

win_width = 10;
overlap = 1;

% nuclei_fr_hist(nuclei)

for nc_id = 1:length(nuclei)
    
    data = load([data_dir,'mat_data/',nuclei{nc_id},'-spikedata']);
    IDsall = double(data.N_ids);
    IDs = IDsall - min(IDsall) + 1;
    spk_times = double(data.spk_times)/10;
%     spk_times_d = double(spk_times);
    numunits = max(IDs) - min(IDs) + 1;
    switch nuclei{nc_id}
        case 'ST'
            STids = STids - min(STall) + 1;
            [subpop_ids,subpop_spktimes] = ...
                spk_id_time_subpop_ex(STids,IDs,spk_times);
%         case 'M2'
%             M2ids = M2ids - min(M2all) + 1;
%             [subpop_ids,subpop_spktimes] = ...
%                 spk_id_time_subpop_ex(M2ids,IDs,spk_times);
%         case 'FS'
%             FSids = FSids - min(FSall) + 1;
%             [subpop_ids,subpop_spktimes] = ...
%                 spk_id_time_subpop_ex(FSids,IDs,spk_times);
    end
    
%     if strcmpi(nuclei{nc_id},'SN')
%         silent_snr_id(IDs,spk_times,fig_dir)
%     end
    
    for st_id = 1:1:length(stimtimes)
        disp([nuclei{nc_id},'-',num2str(st_id)])
        st_time = stimtimes(st_id) - 1000;
        end_time = stimtimes(st_id) + 1000;
        [cnt(st_id,:),cnttimes] = PSTH_mov_win(spk_times,win_width,overlap,st_time,end_time,numunits,1);
%         figure;
%         
%         subplot(211)
%         plot(cnttimes - stimtimes(st_id),cnt,...
%             'LineWidth',2)
%         GCA = gca;
%         GCA.FontSize = 14;
%         GCA.Box = 'off';
%         GCA.TickDir = 'out';        
%         title(['Stimulus max frequency = ',num2str(stimrate(st_id)),' Hz'])
%         
%         subplot(212)
%         spktimes_raster = ...
%             spk_times(spk_times>=st_time & spk_times<=end_time) - stimtimes(st_id);
%         ids_raster = IDs(spk_times>=st_time & spk_times<=end_time);
%         
% %         if strcmpi(nuclei{nc_id},'SN')
% %             silent_snr_id(ids_raster,spktimes_raster,fig_dir)
% %         end
%         if numunits > 10000
%             random_sel = round(numunits/200);
%         elseif numunits > 1000
%             random_sel = round(numunits/20);
%         else
%             random_sel = round(numunits/10);
%         end
%         raster_time_id_nest_rand(spktimes_raster,ids_raster,random_sel,'blue')
%         GCA = gca;
%         GCA.FontSize = 14;
%         GCA.Box = 'off';
%         GCA.TickDir = 'out';
%         title(nuclei{nc_id})
%         fig_print(gcf,[fig_dir,nuclei{nc_id},'-',num2str(stimrate(st_id)),...
%                         '-',num2str(win_width)])
%         close(gcf)
        
        % subpopulation receiving stimuli plot
        
%         if sum(strcmpi(nuclei(nc_id),{'ST'})) > 0
%             num_units_insubpop = length(unique(subpop_ids));
%             [cnt_subpop(st_id,:),cnttimes] = PSTH_mov_win(subpop_spktimes,win_width,overlap,...
%                 st_time,end_time,num_units_insubpop,1);
%             figure;
% 
%             subplot(211)
%             plot(cnttimes - stimtimes(st_id),cnt,...
%                 'LineWidth',2)
%             GCA = gca;
%             GCA.FontSize = 14;
%             GCA.Box = 'off';
%             GCA.TickDir = 'out';        
%             title(['Stimulus max frequency = ',num2str(stimrate(st_id)),' Hz'])
% 
%             subplot(212)
%             spktimes_raster = ...
%                 subpop_spktimes(subpop_spktimes>=st_time & subpop_spktimes<=end_time) - stimtimes(st_id);
%             ids_raster = ids_renum_for_raster(subpop_ids(subpop_spktimes>=st_time & subpop_spktimes<=end_time));        
%             raster_time_id_nest(spktimes_raster,ids_raster,'blue')
%             GCA = gca;
%             GCA.FontSize = 14;
%             GCA.Box = 'off';
%             GCA.TickDir = 'out';
%             title(nuclei{nc_id})
%             fig_print(gcf,[fig_dir,'subpop-',nuclei{nc_id},'-',...
%                             num2str(stimrate(st_id)),'-',num2str(win_width)])
%             close(gcf)
%         end
        
%         pause()
    end
    figure;
    imagesc(cnttimes - stimtimes(st_id),stimrate,cnt)
    GCA = gca;
    GCA.FontSize = 14;
    GCA.Box = 'off';
    GCA.TickDir = 'out';
    xlabel('Time to ramp onset (ms)')
    ylabel('Max input firing rate (Hz)')
    title(nc_names{nc_id})
    ax = colorbar();
    ax.Label.String = 'Average firing rate (Hz)';
    ax.Label.FontSize = 14;
    fig_print(gcf,[fig_dir,'colorplot-',nuclei{nc_id}])
    close(gcf)
    
%     if sum(strcmpi(nuclei(nc_id),{'ST'})) > 0
%         figure;
%         imagesc(cnttimes - stimtimes(st_id),stimrate,cnt_subpop)
%         GCA = gca;
%         GCA.FontSize = 14;
%         GCA.Box = 'off';
%         GCA.TickDir = 'out';
%         xlabel('Time to ramp onset (ms)')
%         ylabel('Max input firing rate (Hz)')
%         title(['subpopulation - ',nc_names{nc_id}])
%         ax = colorbar();
%         ax.Label.String = 'Average firing rate (Hz)';
%         ax.Label.FontSize = 14;
%         fig_print(gcf,[fig_dir,'colorplot-subpop-',nuclei{nc_id}])
%         close(gcf)
%     end
            
end
end

function [ids,spktimes] = spk_id_time_ex(dir)
    data = load(dir);
    IDs = double(data.N_ids);
    ids = IDs - min(IDs);
    spktimes = double(data.spk_times)/10;
%     spk_times_d = double(spk_times);
%    numunits = max(ids) - min(ids) + 1;
end
function [stim_ids,stim_spktimes] = spk_id_time_subpop_ex(subpop_ids,ids,spk_times)
    stim_ids = [];
    stim_spktimes = [];
    for sp_ind = 1:length(subpop_ids)
        stim_ids = [stim_ids;ids(ids == subpop_ids(sp_ind))];
        stim_spktimes = [stim_spktimes;spk_times(ids == subpop_ids(sp_ind))];
    end
end
function renumbered = ids_renum_for_raster(IDs)
    IDs_u = unique(IDs);
    renumbered = IDs;
    for ind = 1:length(IDs_u)
        renumbered(renumbered == IDs_u(ind)) = ind;
    end
end
function [] = silent_snr_id(ids,spk_times,fig_dir)
    ids_u = unique(ids);
    for id_ind = 1:length(ids_u)
        spks_in_id = sort(spk_times(ids==ids_u(id_ind)));
        figure;
        histogram(diff(spks_in_id),[0:10:100])
        GCA = gca;
        GCA.FontSize = 14;
        xlabel('ISI (ms)')
        ylabel('Counts')
        title(['SNr unit # ',num2str(ids_u(id_ind))])
        histdir = [fig_dir,'ISIhist/'];
        if exist(histdir,'dir') ~= 7
            mkdir(histdir)
        end
        fig_print(gcf,[histdir,'ISIhist-SNr-',num2str(ids_u(id_ind))])
        close(gcf)
    end
end
function [] = nuclei_fr_hist(nuclei,fig_dir)
    for nc_id = 1:length(nuclei)
        [IDs,spk_times] = spk_id_time_ex([data_dir,'mat_data/',nuclei{nc_id},'-spikedata']);
        IDs_u = unique(IDs);
        firingrates = zeros(2,length(IDs_u));

        for id_ind = 1:length(IDs_u)
            firingrates(1,id_ind) = IDs(id_ind);
            firingrates(2,id_ind) = sum(IDs == IDs_u(id_ind))/max(spk_times)*1000;
        end

        SUFR(nc_id).nc_name = nuclei(nc_id);
        SUFR(nc_id).fr_ids = firingrates;
        figure;
        histogram(firingrates(2,:),20)
        GCA = gca;
        GCA.FontSize = 14;
        GCA.Box = 'off';
        GCA.TickDir = 'out';
        histdir = [fig_dir,'ISIhist/'];
        fig_print(gcf,[histdir,'hist-',nuclei{nc_id}])
        close(gcf)  
    end
end