%% Date created 28.12.17 by Mohagheghi 

%% Analysis and visualization of spiking data

% This scripts load the data which contains the average firing rate of all
% stimulation paramtere combination across all trials and is going to
% visualize the change in the latency of the decrease in avergae firing
% rate of SNr. The data is stored in "avg_fr_data_eachtr".

function [] = main_SNr_dec_latency_ISI(data_dir,fig_dir)
%     warning('off')
    nc_id = 1;
    nuclei = {'SN','FS','GA','GI','M1','M2','ST'};
    nc_names = {'SNr','FSI','GPe Arky','GPe Proto',...
                'MSN D1','MSN D2','STN'};
    pause_vals = [];
    pause_vals_str = [];
            
    fig_dir = [fig_dir,'latency-comparison-ISI/',nuclei{nc_id},'/'];
    
    if exist(fig_dir,'dir') ~= 7
        mkdir(fig_dir)
    end

%     start_search_time = -150;                   % Time to look for the decrease

    avgfr_data = load([data_dir,'avg_fr_data_eachtr_ISI']);
    off_time = avgfr_data.off_time;
    off_time_str = avgfr_data.off_time_str;
    params = avgfr_data.params;
%     t_vec = avgfr_data.t_samples;
    
%     cnt = cnt(:,t_vec >= start_search_time);
%     cnt_str = cnt_str(:,t_vec >= start_search_time);
%     t_vec = t_vec(t_vec >= start_search_time);
    
    stn_f = unique(params(:,1));
    rel_time = unique(params(:,2));
    str_f = unique(params(:,3));
    tr_vec = unique(params(:,4));
    
%     SNr_fr_th = 2;                  % Threshold for the SNr movement trigger
    width_th = 20;
    
    for strf_ind = 1:length(str_f)
        for stnf_ind = 1:length(stn_f)
            for relt_ind = 1:length(rel_time)
                sel_inds = find(params(:,1) == stn_f(stnf_ind) & ...
                                params(:,2) == rel_time(relt_ind) & ...
                                params(:,3) == str_f(strf_ind));
%                 for inds = 1:length(sel_inds)
                cnt_time = off_time(sel_inds);
                cnt_str_time = off_time_str(sel_inds);
%                 end
                num_suppressed_mov(stnf_ind,relt_ind,strf_ind) = sum(~isnan(cnt_str_time)) - ...
                                     sum(~isnan(cnt_time));
                time_diff = cnt_time - cnt_str_time;
                time_diff_avg(stnf_ind,relt_ind,strf_ind) = mean(time_diff(~isnan(time_diff)));
                time_pos_diff_avg(stnf_ind,relt_ind,strf_ind) = mean(time_diff(~isnan(time_diff) & ...
                                                                              (time_diff>=0)));
                num_non_nan(stnf_ind,relt_ind,strf_ind) = sum(~isnan(time_diff));
                                
            end
        end
        figure;
        imagesc(rel_time,stn_f,time_diff_avg(:,:,strf_ind))
        GCA = gca;
        GCA.FontSize = 14;
        GCA.Box = 'off';
        GCA.TickDir = 'out';
        xlabel('Time to ramp offset (ms)')
        ylabel('Max input firing rate to STN (Hz)')
        title([nc_names{nc_id},...
            '-STR = ',num2str(str_f(strf_ind)),' (Hz)'])
        ax = colorbar();
        ax.Label.String = 'Time difference in Stop - Go experiment (ms)';
        ax.Label.FontSize = 14;
        fig_print(gcf,[fig_dir,'STR-',num2str(str_f(strf_ind))])
        close(gcf)
        
        figure;
        imagesc(rel_time,stn_f,num_non_nan(:,:,strf_ind),[0,100])
        GCA = gca;
        GCA.FontSize = 14;
        GCA.Box = 'off';
        GCA.TickDir = 'out';
        xlabel('Time to ramp offset (ms)')
        ylabel('Max input firing rate to STN (Hz)')
        title([nc_names{nc_id},...
            '-STR = ',num2str(str_f(strf_ind)),' (Hz)'])
        ax = colorbar();
        ax.Label.String = 'Number of Samples';
        ax.Label.FontSize = 14;
        fig_print(gcf,[fig_dir,'numsamples-',num2str(str_f(strf_ind))])
        close(gcf)
        
        figure;
        imagesc(rel_time,stn_f,num_suppressed_mov(:,:,strf_ind))
        GCA = gca;
        GCA.FontSize = 14;
        GCA.Box = 'off';
        GCA.TickDir = 'out';
        xlabel('Time to ramp offset (ms)')
        ylabel('Max input firing rate to STN (Hz)')
        title([nc_names{nc_id},...
            '-STR = ',num2str(str_f(strf_ind)),' (Hz)'])
        ax = colorbar();
        ax.Label.String = 'Number of suppressed movements';
        ax.Label.FontSize = 14;
        fig_print(gcf,[fig_dir,'numsuppsamples-',num2str(str_f(strf_ind))])
        close(gcf)
        
        figure;
        imagesc(rel_time,stn_f,time_pos_diff_avg(:,:,strf_ind))
        GCA = gca;
        GCA.FontSize = 14;
        GCA.Box = 'off';
        GCA.TickDir = 'out';
        xlabel('Time to ramp offset (ms)')
        ylabel('Max input firing rate to STN (Hz)')
        title([nc_names{nc_id},...
            '-STR = ',num2str(str_f(strf_ind)),' (Hz)'])
        ax = colorbar();
        ax.Label.String = 'Time difference in Stop - Go experiment (ms)';
        ax.Label.FontSize = 14;
        fig_print(gcf,[fig_dir,'STR-',num2str(str_f(strf_ind)),'-posdiff'])
        close(gcf)
    end
    save([fig_dir,'latency-var-peakth',num2str(SNr_fr_th),'-widthth',num2str(width_th)],...
         'time_diff_avg','num_non_nan','num_suppressed_mov')
end

function [disinh_ind,width] = disinhibition_find(signal,th,w_th)
%     signal = -signal;
    [~,ind,width,~] = findpeaks(-signal,'MinPeakHeight',-th,'MinPeakWidth',w_th);
%     [max_val,max_w_ind] = max(width);
    if ~isempty(ind)
        disinh_ind = ind(1);
    else
        disinh_ind = ind;
    end
end