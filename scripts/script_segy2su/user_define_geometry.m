%% Matlab script to setup 2D geometry for model with topography
% The depth of the sources and receivers is defined by topography file
% Wenbin Jiang
% 2019.04.03
%% Parameters defined by user
ns  = 40;             % source numbei r
sx0 = 300;               % location of the first source, X
sz0 = 10;               % location of the firsr source, Z (sz is ignored if source_surf is set to true, it is replaced with the topography height)
dsx = 600;               % source interval, X
dsz = 0;               % source interval, Z

nr  = 410;            % receiver number
rx0 = 150;               % location of the first receiver, X
rz0 = 10;               % location of the firsr receiver, Z
drx = 60;               % receiver interval, X
drz = 0;               % receiver interval, Z

source_surf = true;        % source inside the medium, or source automatically moved exactly at the surface by the solver
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

%% Load topography file
%topo=load('topo.top');

%% Output geometry file
if ~exist('./geometry_files','dir')==0
	rmdir('./geometry_files','s');
end

mkdir('./geometry_files');

% SOURCE
filename = sprintf('./geometry_files/source.dat');
fid=fopen(filename,'w');
for is=1:ns
	fprintf(fid,'%f \t',sx0+(is-1)*dsx);
	fprintf(fid,'%f \n',sz0+(is-1)*dsz);
end
fclose(fid);

% output the source info into different SOURCE files
for is=1:ns
	filename = sprintf('./geometry_files/SOURCE_%06i',is-1);
    fid=fopen(filename,'w');
	
	if source_surf == 0
		fprintf(fid,'source_surf = .false. \n');
	else
		fprintf(fid,'source_surf = .true. \n');
	end
	
	fprintf(fid,'xs = %f \n',sx0+(is-1)*dsx);
	fprintf(fid,'zs = %f \n',sz0+(is-1)*dsz);
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
end

%% STATIONS
%filename = sprintf('./geometry_files/STATIONS');
%fid=fopen(filename,'w');
%
%% station network latitude longitude elevation(m) burial(m)
%for ir=1:nr
%	fprintf(fid,'S%06i ',ir-1);
%	fprintf(fid,'AA ');
%	fprintf(fid,'%f ',rx0+(ir-1)*drx);
%	fprintf(fid,'%f ',rz0+(ir-1)*drz);
%	fprintf(fid,'%f ',0.0);
%	fprintf(fid,'%f \n',0.0);
%end



