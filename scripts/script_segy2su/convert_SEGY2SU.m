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

%% geometry parameters defined by user
source_surf = false;        % source inside the medium, or source automatically moved exactly at the surface by the solver
source_type = 1;            % source type: elastic force or acoustic pressure = 1 or moment tensor = 2; For a plane wave including converted ;and reflected waves at the free surface, P wave = 1, S wave = 2, Rayleigh wave = 3 For a plane wave without converted nor reflected waves at the free surface, i.e. with the incident wave only, P wave = 4, S wave = 5
time_function_type = 1;     % second derivative of a Gaussian (a.k.a. Ricker) = 1, first derivative of a Gaussian = 2, Gaussian = 3, Dirac = 4, Heaviside = 5 (4 and 5 will produce noisy recordings because of frequencies above the mesh resolution limit). time function_type == 8 source read from file, if time function_type == 9 : burst; If time_function_type == 8, enter below the custom source file to read (two columns file with time and amplitude) : (For the moment dt must be equal to the dt of the simulation. File name cannot exceed 150 characters). IMPORTANT: do NOT put quote signs around the file name, just put the file name itself otherwise the run will stop
name_of_source_file             = 'YYYYYYYYYYYYYYYYYY';             % Only for option 8 : file containing the source wavelet
burst_band_width                = 0.0;             % Only for option 9 : band width of the burst
f0                              = 10.0;           % dominant source frequency (Hz) if not Dirac or Heaviside
tshift                          = 0.0;            % time shift when multi sources (if one source, must be zero)
anglesource                     = 0.0;             % angle of the source (for a force only); for a plane wave, this is the incidence angle; for moment tensor sources this is unused
Mxx                             = 1.0;             % Mxx component (for a moment tensor source only)
Mzz                             = 1.0;             % Mzz component (for a moment tensor source only)
Mxz                             = 0.0;             % Mxz component (for a moment tensor source only)
factor                          = 1.d10;          % amplification factor
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
    sourceX=cat(1,SegyTraceHeader.SourceX);
    sourceY=cat(1,SegyTraceHeader.SourceY);
    GroupX=cat(1,SegyTraceHeader.GroupX);
    GroupY=cat(1,SegyTraceHeader.GroupY);
    source_elevation=cat(1,SegyTraceHeader.SourceSurfaceElevation);
    Group_elevation =cat(1,SegyTraceHeader.ReceiverGroupElevation);
	
    shotX=sourceX(1)/100; % unit is m
	shotY=sourceY(1)/100; % unit is m
	shotZ=-source_elevation(1)/100; % unit is m
	for irec=1:trace_num_pershot(ishot)
        recX(irec)=GroupX(irec)/100;
        recY(irec)=GroupY(irec)/100;
        recZ(irec)=-Group_elevation(irec)/100;
    end
    
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
    
    % Output geometry file
    if ~exist('./geometry_files','dir')==0
        rmdir('./geometry_files','s');
    end

    mkdir('./geometry_files');
    % Output SOURCE file
    filename = sprintf('./geometry_files/SOURCE_%06i',ishot-1);
    fid=fopen(filename,'w');
	
	if source_surf == 0
		fprintf(fid,'source_surf = .false. \n');
	else
		fprintf(fid,'source_surf = .true. \n');
	end
	
	fprintf(fid,'xs = %f \n',shotX);
	fprintf(fid,'zs = %f \n',shotZ);
	fprintf(fid,'source_type = %d \n',source_type);
	fprintf(fid,'time_function_type = %d \n',time_function_type);
	fprintf(fid,'name_of_source_file = %s \n',name_of_source_file);
	fprintf(fid,'burst_band_width = %f \n',burst_band_width);
	fprintf(fid,'f0 = %f \n',f0);
	fprintf(fid,'tshitf = %f \n',tshift);
	fprintf(fid,'anglesource = %f \n',anglesource);
	fprintf(fid,'Mxx = %f \n',Mxx);
	fprintf(fid,'Mzz = %f \n',Mzz);
	fprintf(fid,'Mxz = %f \n',Mxz);
	fprintf(fid,'factor = %f \n',factor);
	fclose(fid);
    
    % Output STATIONS file
    filename = sprintf('./geometry_files/STATIONS_%06i',ishot-1);
    fid=fopen(filename,'w');
    for irec=1:trace_num_pershot(ishot)
        fprintf(fid,'S%04i ',irec-1);
        fprintf(fid,'AA ');
        fprintf(fid,'%f ',recX(irec));
        fprintf(fid,'%f ',recZ(irec));
        fprintf(fid,'%f ',0.0);
        fprintf(fid,'%f \n',0.0);
    end
    
end
