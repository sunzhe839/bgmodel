%% Date Created: 12.04.18 by M. Mohagheghi

% This script visualizes the average firing rates based on the
% specificities given to it. These specificieties are stimulation
% strengthes, relative time of the stimulations and trial, nucleus index
% plus weight. Note that the current average firing rates in the data
% stored after preprocessing is the binned version of spike times without
% any overlap.

function [f_color,f_trace,f_spec] = main_avgfr(stim_w_pars,trials,STR,STN,GPA,t_vec,w_width)
    if ~isempty(GPA)
        [f_color,f_trace,f_spec] = avgfr(stim_w_pars,trials,STR,STN,GPA,t_vec,w_width);
    else
        [f_color,f_trace,f_spec] = avgfr_stn(stim_w_pars,trials,STR,STN,t_vec,w_width);
    end
end

function [f_color,f_trace,f_spec] = avgfr(stim_w_pars,trials,STR,STN,GPA,time_vec,w_width)

    fs = 1000;
    [wav_kernel,freqs] = mor_wav_gen_intfreq_Friston(fs);

    disp(stim_w_pars)

    for nc_ind = 1:length(STR.nuclei)
        NC{nc_ind} = STR.nuclei(nc_ind).nc_names;
    end
    nc_ids = unique(STR.nuclei_trials(:,1));
    
    % Assuring to avoid 0s in nc_ids. The reason they appear is that there
    % is predefinition of variables when data is being processed and
    % therefore some zeros are extra in the data stored.
    
    nc_ids(nc_ids == 0) = [];
    
    %%%
    
    order_vis_ncs = {'GA','M1','M1','FS','SN','GI','ST'};%{'FS','M2','GI','GA','M1','SN','ST'};
    nuclei_names  = {'GPe Arky','MSN D1','MSN D1','FSI','SNr','GPe Proto','STN'};
    numunits = [41,4746,4746,200,94,111,49];%[200,4767,111,41,4746,94,49];

    for stim_ind = 1:size(stim_w_pars,1)
        f_trace = figure;
        subplot(4,2,1)
        f_spec  = figure;
        for nc_ind = 1:length(order_vis_ncs)
            region_id = nc_ids(strcmpi(NC,order_vis_ncs{nc_ind}));
            bindat_id = GPA.stim_param(:,2) == stim_w_pars(stim_ind,1) & ...
                        GPA.stim_param(:,3) == stim_w_pars(stim_ind,2) & ...
                        GPA.stim_param(:,1) == stim_w_pars(stim_ind,3) & ...
                        GPA.stim_param(:,5) == stim_w_pars(stim_ind,4) & ...
                        GPA.stim_param(:,4) == stim_w_pars(stim_ind,5) & ...
                        GPA.nuclei_trials(:,3) == stim_w_pars(stim_ind,6) & ...
                        GPA.nuclei_trials(:,1) == region_id;
            bindat_tmp = GPA.average_fr_no_overlap(bindat_id,:);
            avg_fr_noovr = GPA.average_fr_no_overlap(bindat_id,:);
%             numunits = unique(GPA.num_units(bindat_id));
            trials_m = missing_tr_find(bindat_tmp,trials,GPA.nuclei_trials(bindat_id,2));
            if isempty(trials_m)
                bindat_tmp = zeros(1,size(bindat_tmp,2));
                trials_m = 1;
            end
                [gpa_avgfr,gpa_avgfr_z(nc_ind,:)] = average_fr(bindat_tmp(trials_m,:),numunits(nc_ind),w_width);
%             size(trials_m)
%             size(bindat_tmp)

            bindat_id = STN.stim_param(:,1) == stim_w_pars(stim_ind,1) & ...
                        STN.stim_param(:,2) == stim_w_pars(stim_ind,2) & ...
                        STN.stim_param(:,3) == stim_w_pars(stim_ind,4) & ...
                        STN.nuclei_trials(:,3) == stim_w_pars(stim_ind,6) & ...
                        STN.nuclei_trials(:,1) == region_id;
            bindat_tmp = STN.average_fr_no_overlap(bindat_id,:);
            
            trials_m = missing_tr_find(bindat_tmp,trials,GPA.nuclei_trials(bindat_id,2));
            [stn_avgfr,stn_avgfr_z(nc_ind,:)] = average_fr(bindat_tmp(trials_m,:),numunits(nc_ind),w_width);

            bindat_id = STR.stim_param(:,1) == stim_w_pars(stim_ind,1) & ...
                        STR.nuclei_trials(:,3) == stim_w_pars(stim_ind,6) & ...
                        STR.nuclei_trials(:,1) == region_id;
            bindat_tmp = STR.average_fr_no_overlap(bindat_id,:);
            trials_m = missing_tr_find(bindat_tmp,trials,GPA.nuclei_trials(bindat_id,2));
            [str_avgfr,str_avgfr_z(nc_ind,:)] = average_fr(bindat_tmp(trials_m,:),numunits(nc_ind),w_width);

            if nc_ind ~= 2
                figure(f_spec)
                subplot(4,2,nc_ind)
                S = avgfr_spectrogram(avg_fr_noovr,numunits(nc_ind),wav_kernel,w_width);
                if isempty(S)
                    disp(['S is empty! for ', order_vis_ncs{nc_ind}])
                else
                    [CA] = spec_vis(S,time_vec,freqs);
                    CA.Title.String = order_vis_ncs{nc_ind};
                end
            end

            figure(f_trace)
            subplot(4,2,nc_ind)
            avgfr_vis_trace(f_trace,nc_ind,gpa_avgfr,time_vec,order_vis_ncs,'red');
            hold on
            avgfr_vis_trace(f_trace,nc_ind,stn_avgfr,time_vec,order_vis_ncs,'blue');
            [CA] = avgfr_vis_trace(f_trace,nc_ind,str_avgfr,time_vec,order_vis_ncs,'green');
            CA.Title.String = nuclei_names{nc_ind};
            
        end
        LH = legend({'GPA+STN','STN','No Sen.'});
        LH.Box = 'off';
        f_trace.Position = f_trace.Position .* [1,1,2,2];
        f_spec.Position = f_spec.Position .* [1,1,2,2];
        f_color = figure;
%         subplot(3,1,1)
        numsub = 3;
        CA = avgfr_vis_color(f_color,numsub,1,gpa_avgfr_z,time_vec,nuclei_names);
        CA.Title.String =   ['W='   ,num2str(stim_w_pars(stim_ind,6)),' ;',...
                             'STR=' ,num2str(stim_w_pars(stim_ind,1)),' ;',...
                             'STN=' ,num2str(stim_w_pars(stim_ind,2)),' ;',...
                             'GPA=' ,num2str(stim_w_pars(stim_ind,3)),' ;',...
                             'RSS=' ,num2str(stim_w_pars(stim_ind,4)),' ;',...
                             'RSG=' ,num2str(stim_w_pars(stim_ind,5))];
        CA = avgfr_vis_color(f_color,numsub,2,stn_avgfr_z,time_vec,nuclei_names);
        CA = avgfr_vis_color(f_color,numsub,3,str_avgfr_z,time_vec,nuclei_names);
%         CA = avgfr_vis_color(f_color,2,stn_avgfr_z,[-495:495],order_vis_ncs);
%         CA = avgfr_vis_color(f_color,3,str_avgfr_z,[-495:495],order_vis_ncs);
        CA.XLabel.String = 'Time from ramp offset (ms)';
        f_color.Position = f_color.Position .* [1,1,2,2];
    end
end
function [f_color,f_trace,f_spec] = avgfr_stn(stim_w_pars,trials,STR,STN,time_vec,w_width)
    disp(stim_w_pars)

    fs = 1000;
    [wav_kernel,freqs] = mor_wav_gen_intfreq_Friston(fs);

    for nc_ind = 1:length(STR.nuclei)
        NC{nc_ind} = STR.nuclei(nc_ind).nc_names;
    end
    nc_ids = unique(STR.nuclei_trials(:,1));
    order_vis_ncs = {'GA','M1','M1','FS','SN','GI','ST'};%{'FS','M2','GI','GA','M1','SN','ST'};
    nuclei_names  = {'GPe Arky','MSN D1','MSN D1','FSI','SNr','GPe Proto','STN'};
    numunits = [41,4746,4746,200,94,111,49];%[200,4767,111,41,4746,94,49];

    for stim_ind = 1:size(stim_w_pars,1)
        f_trace = figure;
        subplot(4,2,1)
        f_spec  = figure;
        for nc_ind = 1:length(order_vis_ncs)
            region_id = nc_ids(strcmpi(NC,order_vis_ncs{nc_ind}));
            bindat_id = STN.stim_param(:,1) == stim_w_pars(stim_ind,1) & ...
                        STN.stim_param(:,2) == stim_w_pars(stim_ind,2) & ...
                        STN.stim_param(:,3) == stim_w_pars(stim_ind,3) & ...
                        STN.nuclei_trials(:,3) == stim_w_pars(stim_ind,4) & ...
                        STN.nuclei_trials(:,1) == region_id;
            bindat_tmp = STN.average_fr_no_overlap(bindat_id,:);
            avg_fr_noovr = STN.average_fr_no_overlap(bindat_id,:);
            
            trials_m = missing_tr_find(bindat_tmp,trials,STN.nuclei_trials(bindat_id,2));
            [stn_avgfr,stn_avgfr_z(nc_ind,:)] = average_fr(bindat_tmp(trials_m,:),numunits(nc_ind),w_width);

            bindat_id = STR.stim_param(:,1) == stim_w_pars(stim_ind,1) & ...
                        STR.nuclei_trials(:,3) == stim_w_pars(stim_ind,4) & ...
                        STR.nuclei_trials(:,1) == region_id;
            bindat_tmp = STR.average_fr_no_overlap(bindat_id,:);
            trials_m = missing_tr_find(bindat_tmp,trials,STN.nuclei_trials(bindat_id,2));
            [str_avgfr,str_avgfr_z(nc_ind,:)] = average_fr(bindat_tmp(trials_m,:),numunits(nc_ind),w_width);

            if nc_ind ~= 2
                figure(f_spec)
                subplot(4,2,nc_ind)
                S = avgfr_spectrogram(avg_fr_noovr,numunits(nc_ind),wav_kernel,w_width);
                if isempty(S)
                    disp(['S is empty! for ', order_vis_ncs{nc_ind}])
                else
                    [CA] = spec_vis(S,time_vec,freqs);
                    CA.Title.String = order_vis_ncs{nc_ind};
                end
            end

            figure(f_trace)
            subplot(4,2,nc_ind)
            avgfr_vis_trace(f_trace,nc_ind,stn_avgfr,time_vec,order_vis_ncs,'blue');
            hold on
            [CA] = avgfr_vis_trace(f_trace,nc_ind,str_avgfr,time_vec,order_vis_ncs,'green');
            CA.Title.String = nuclei_names{nc_ind};
           
        end
        LH = legend({'STN','No Sen.'});
        LH.Box = 'off';
        f_trace.Position = f_trace.Position .* [1,1,2,2];
        f_spec.Position = f_spec.Position .* [1,1,2,2];
        f_color = figure;
%         subplot(3,1,1)
        numsub = 2;
        CA = avgfr_vis_color(f_color,numsub,1,stn_avgfr_z,time_vec,nuclei_names);
        CA.Title.String =   ['W='   ,num2str(stim_w_pars(stim_ind,4)),' ;',...
                             'STR=' ,num2str(stim_w_pars(stim_ind,1)),' ;',...
                             'STN=' ,num2str(stim_w_pars(stim_ind,2)),' ;',...
                             'RSS=' ,num2str(stim_w_pars(stim_ind,3)),' ;'];
        CA = avgfr_vis_color(f_color,numsub,2,str_avgfr_z,time_vec,nuclei_names);
%         CA = avgfr_vis_color(f_color,2,stn_avgfr_z,[-495:495],order_vis_ncs);
%         CA = avgfr_vis_color(f_color,3,str_avgfr_z,[-495:495],order_vis_ncs);
        CA.XLabel.String = 'Time from ramp offset (ms)';
        f_color.Position = f_color.Position .* [1,1,2,2];
    end
end

function [SPEC] = avgfr_spectrogram(binned_dat,NU,wavlt,win_w)
    binned_dat = double(binned_dat);
    binned_dat = mean(binned_dat);
    mov_win_avgfr = overlap_hamming(binned_dat,win_w)/double(NU);
    z_score = zscore(mov_win_avgfr);
    %S = spectrogram_int_freqs(binned_dat,wavlt);
    S = spectrogram_int_freqs(z_score,wavlt);
    SPEC = 10*log10(abs(S));
end

function [mov_win_avgfr,z_score] = average_fr(all_bindata,NU,win_w)
    all_bindata = double(all_bindata);
    if size(all_bindata,1) > 1
        all_bindata = mean(all_bindata);
        mov_win_avgfr = overlap_square(all_bindata,win_w)/double(NU);
        z_score = zscore(mov_win_avgfr);
    elseif isempty(all_bindata)
        mov_win_avgfr = 0;
        z_score = 0;
    else
        mov_win_avgfr = overlap_square(all_bindata,win_w)/double(NU);
        z_score = zscore(mov_win_avgfr);
    end
end

function smoothed_data = overlap_square(binned_data,win_width)
    win = ones(1,win_width)/win_width;
    tmp_smth = conv(binned_data,win,'same');
    smoothed_data = tmp_smth(win_width/2:end-(win_width/2));
end

function smoothed_data = overlap_hamming(binned_data,win_width)
    win = hamming(win_width);
    win = win/sum(win);
    tmp_smth = conv(binned_data,win,'same');
    smoothed_data = tmp_smth(win_width/2:end-(win_width/2));
end

function [GCA] = avgfr_vis_color(figid,n_subp,subid,avg_data,t_vec,ord_ncs)
    IND = t_vec>=-150 & t_vec<=100;
    t_vec = t_vec(IND);
    avg_data = avg_data(:,IND);
    figure(figid);
    subplot(n_subp,1,subid)
    imagesc(t_vec,1:length(ord_ncs),avg_data)
    ch = colorbar();
    ch.TickDirection = 'out';
    ch.Box = 'off';
    GCA = gca;
    GCA.TickDir = 'out';
    GCA.Box = 'off';
    GCA.FontSize = 14;
    GCA.YTick = 1:length(ord_ncs);
    for nc_ind = 1:length(ord_ncs)
        GCA.YTickLabel{nc_ind} = ord_ncs{nc_ind};
    end


end

function [GCA] = spec_vis(spctr,t_vec,freqs)
    IND = t_vec>=-200 & t_vec<=100;
%     t_vec = t_vec(IND);
%     avg_data = avg_data(:,IND);
%     xlim([-150,100])
%     figure(figid);
%     subplot(4,2,subid)
    disp(['max spctr is ',num2str(max(spctr(:)))])
    imagesc(t_vec,freqs,spctr,[-20,max(spctr(:))])
    ylim([0,100])
    xlim([-200,100])
    GCA = gca;
    GCA.TickDir = 'out';
    GCA.Box = 'off';
    GCA.FontSize = 14;
    col_ax = colorbar();
    col_ax.TickDirection = 'out';
    col_ax.Title.String = 'Power';
end

function [GCA] = avgfr_vis_trace(figid,subid,avg_data,t_vec,ord_ncs,Col)
    IND = t_vec>=-150 & t_vec<=100;
    t_vec = t_vec(IND);
    avg_data = avg_data(:,IND);
    xlim([-150,100])
    figure(figid);
%     subplot(4,2,subid)
    plot(t_vec,avg_data,'LineWidth',2,'Color',Col)
    GCA = gca;
    GCA.TickDir = 'out';
    GCA.Box = 'off';
    GCA.FontSize = 14;
end

function sel_trs = missing_tr_find(bind,sel_trs,trials_)
    if size(bind,1) < max(sel_trs)
        tr_vec = 1:99;
        tr_vec(trials_) = [];
        disp(['Missing trial numbers ',num2str(tr_vec)])
    end
    while size(bind,1) < max(sel_trs)
%         disp('Missing trial!')
        sel_trs(find(sel_trs==max(sel_trs))) = [];
%         missing_tr_find(bind,sel_trs,trials_);
    end
end