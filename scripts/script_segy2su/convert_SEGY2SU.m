%% Read SEGY data and convert it to SU format for SeisFlows
clear; close all; clc;
%% read seismic data
%filename_input_segy='./Alfonsine_offset1200.sgy';
%shot_num = 2162; % shot number
filename_input_segy='002.segy';
shot_num=1;
trace_num = 96; % trace number per shot
dt=4; % unit=ms 
%%
[Data_2d]=ReadSegyFast(filename_input_segy);
disp('read Data_2d end');
shotID=ReadSegyTraceHeaderValue(filename_input_segy,'key','FieldRecord');
disp('read shotID end');
% read header info
% sourceX=cat(1,SegyTraceHeader.SourceX);
% sourceY=cat(1,SegyTraceHeader.SourceY);
% GroupX=cat(1,SegyTraceHeader.GroupX);
% GroupY=cat(1,SegyTraceHeader.GroupY);
% shotID=cat(1,SegyTraceHeader.FieldRecord);
% source_elevation=cat(1,SegyTraceHeader.SourceSurfaceElevation);
% Group_elevation =cat(1,SegyTraceHeader.ReceiverGroupElevation);
%% calculate how many traces per shot
[~,N] = size(Data_2d);

tmp=shotID(1);
itmp=0;ishot=1;
trace_num_pershot=zeros(shot_num,1);
for itrace=1:N
    if(shotID(itrace)~=tmp)
        trace_num_pershot(ishot)=itmp;
        itmp=1;ishot=ishot+1;
        tmp=shotID(itrace);
    else
        itmp=itmp+1;
    end
end
trace_num_pershot(shot_num)=N-sum(trace_num_pershot(1:shot_num-1)); % last shot
%% read one shot once a time
tmp=1;
%for ishot=1:shot_num
for ishot=1:1
    disp(ishot);
    [Data,SegyTraceHeader,SegyHeader] = ReadSegy(filename_input_segy,'traces',[tmp:tmp+trace_num_pershot(ishot)-1]);
    tmp=tmp+trace_num_pershot(ishot);
    
%     % get headervalue
%     SourceX=ReadSegyTraceHeaderValue(filename_input_segy,'key','SourceX');
%     SourceY=ReadSegyTraceHeaderValue(filename_input_segy,'key','SourceY');
% 	GroupX=ReadSegyTraceHeaderValue(filename_input_segy,'key','GroupX');
%     GroupY=ReadSegyTraceHeaderValue(filename_input_segy,'key','GroupY');
% 	SourceSurfaceElevation=ReadSegyTraceHeaderValue(filename_input_segy,'key','SourceSurfaceElevation');
%     ReceiverGroupElevation=ReadSegyTraceHeaderValue(filename_input_segy,'key','ReceiverGroupElevation');
%     % change headervalue
%     SourceX=SourceX./100;
%     SourceY=SourceY./100;
%     GroupX=GroupX./100;
%     GroupY=GroupY./100;  
%     SourceSurfaceElevation=SourceSurfaceElevation./100;
%     ReceiverGroupElevation=ReceiverGroupElevation./100;
%     % update headervalue
%     WriteSegyTraceHeaderValue(filename_input_segy,SourceX,'key','SourceX');
% 	WriteSegyTraceHeaderValue(filename_input_segy,SourceY,'key','SourceY');
%     WriteSegyTraceHeaderValue(filename_input_segy,GroupX,'key','GroupX');
% 	WriteSegyTraceHeaderValue(filename_input_segy,SourceY,'key','GroupY');
%     WriteSegyTraceHeaderValue(filename_input_segy,SourceSurfaceElevation,'key','SourceSurfaceElevation');
% 	WriteSegyTraceHeaderValue(filename_input_segy,ReceiverGroupElevation,'key','ReceiverGroupElevation');    
    
    % Output as SU format
    filepath=['./obs/',num2str(ishot,'%06d'),'/'];
    if ~exist(filepath) 
        mkdir(filepath)         
    else
        rmdir(filepath,'s')
        mkdir(filepath) 
    end 
    WriteSuStructure([filepath,'Uz_file_single.su'],SegyTraceHeader,Data,SegyHeader);
end
