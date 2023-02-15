addpath('F:\data')
path = 'F:\data\GC225\';

mkdir([path 'python'])

lst = dir(path);
for j = 1:length(lst)
    if contains(lst(j).name, 'allData.mat')
        load([lst(j).folder '\' lst(j).name])
        namesplit = split(lst(j).name, '_');
        mkdir([path 'python\' strjoin(namesplit(2:4), '_')])
        
        % Get neural data
        lyrs = size(obj.units,2);
        for i = 1:lyrs
            center = obj.units{1, i}.center;
            dff = obj.units{1, i}.Dff;
            skew = obj.units{1, i}.Skew;

            save([path, 'python\' strjoin(namesplit(2:4), '_') '\layer_', int2str(i), '.mat'], 'center', 'dff', 'skew')
        end 

        % Get behavioral data
        
        obj.Alarm_Nums();
        obj.Pole_Time();
        obj.Cue_Time();
        
        R_hit_tmp = ((char(obj.sides)=='r') & obj.trials.hitHistory);
        R_miss_tmp = ((char(obj.sides)=='r') & obj.trials.missHistory);
        R_ignore_tmp = ((char(obj.sides)=='r') & obj.trials.noResponseHistory);
        L_hit_tmp = ((char(obj.sides)=='l') & obj.trials.hitHistory);
        L_miss_tmp = ((char(obj.sides)=='l') & obj.trials.missHistory);
        L_ignore_tmp = ((char(obj.sides)=='l') & obj.trials.noResponseHistory);
        
        
        LickEarly_tmp = zeros(length(obj.eventsHistory),1);
        LickEarly_tmp(obj.trials.alarmNums,1) = 1;

        % Get i good trials

        StimTrials_tmp = obj.stimProb;
        i_performing = find(StimTrials_tmp>0);
        if ~isempty(i_performing)
            StimTrialsFlag_tmp = StimTrials_tmp;
            seg_break_pt = i_performing(diff(i_performing)>1);
            seg_break_pt = [seg_break_pt; i_performing(end)];
        
            for i_tmp = seg_break_pt'
                if i_tmp<6
                    StimTrialsFlag_tmp(1:i_tmp) = 0;
                else
                    StimTrialsFlag_tmp(i_tmp-5:i_tmp) = 0;
                end
            end
        
            i_good_trials = find(StimTrialsFlag_tmp>0);
        else
            i_good_trials = [];
        end

        % Stim information

        total_trials = obj.trials.trialNums;
        for i_solo_trial = 1:total_trials
    
            % get AOM and Galvo info from wavesurfer
            if size(obj.wavesurfer.timestamp,1)>=i_solo_trial
                wave_time_tmp = obj.wavesurfer.timestamp(i_solo_trial,:);
                wave_aom_tmp = obj.wavesurfer.aom_input_trace(i_solo_trial,:);

            else
                wave_time_tmp = 0;
                wave_aom_tmp = 0;
                wave_xGalvo_tmp = 0;
                wave_yGalvo_tmp = 0;
            end
            
            
            % laser attributes
            AOM_input_tmp = round(max(wave_aom_tmp)*10)/10;
            AOM_data_tmp(i_solo_trial,:) = AOM_input_tmp;
            
            if AOM_input_tmp>0
                i_laser_on = find(wave_aom_tmp>.05);
                t_laser_on = wave_time_tmp(i_laser_on(1));
                t_laser_off = wave_time_tmp(i_laser_on(end));
                
                StimDur_tmp(i_solo_trial,:) = round((t_laser_off-t_laser_on)*10)/10;
                StimOnTime_tmp(i_solo_trial,:) = t_laser_on;
            else
                StimDur_tmp(i_solo_trial,:) = 0;
                StimOnTime_tmp(i_solo_trial,:) = 0;
            end
                        
        end





        save([path 'python\' strjoin(namesplit(2:4), '_') '\behavior.mat'], 'R_hit_tmp', 'R_miss_tmp', 'R_ignore_tmp', 'L_hit_tmp', 'L_miss_tmp', 'L_ignore_tmp', 'LickEarly_tmp', 'i_good_trials', 'StimDur_tmp')
        
        clearvars AOM_data_tmp StimDur_tmp StimOnTime_tmp

    end
end