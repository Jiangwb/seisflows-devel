%% plot model
clear; clc; close all;
% gaussian function to mask source effect
r=600; % sigma usually equals to 20 times of a grid size
sigma=200; % sigma usually equals to 5 times of a grid size
GaussTemp = ones(1,r*2-1);
for i=1 : r*2-1
    GaussTemp(i) = exp(-(i)^2/(2*sigma^2))/(sigma*sqrt(2*pi));
end
Gauss=GaussTemp;
for i=1 : r*2-1
    Gauss(i) = 1-Gauss(i)./max(GaussTemp);
end
for i=1 : r*2-1
    Gauss(i) = Gauss(i).^4;
end
figure(1);plot(Gauss);
%% read data
data=load('proc000000_model_velocity.dat_input');
[row column]=size(data);
x_max=max(data(:,2));
z_max=max(data(:,3));
% read source location
source=load('source.dat');
[nsource,~]=size(source);
%% mask according to the source location
% find topography
x=unique(data(:,2));
[x_num,~]=size(x);
z=zeros(1,x_num);
for i=1:x_num
    z_tmp=zeros(1,100000);
    for j=1:row
        k=1;
        if data(j,2)==x(i)
           z_tmp(k)=data(j,3);
           k=k+1;
        end
    end
	z(i)=max(z_tmp); % z is topography
end

% source depth is defined by topography
for isource=1:nsource
    source_x(isource)=source(isource,1);
    for ix=1:x_num
        dist(ix)=abs(source_x(isource)-x(ix));
    end
    [~,index]=min(dist);
    source_z(isource)=z(index);
end

% set mask (source depth is defined by topography)
mask=zeros(row,column-1,nsource);
for isource=1:nsource
    for irow=1:row
        dist=sqrt((source_x(isource)-data(irow,2)).^2+(source_z(isource)-data(irow,3)).^2);
        if dist<=2*r-2
            mask(irow,5,isource)=Gauss(round(dist+1));
        else
            mask(irow,5,isource)=1;
        end
    end
end
mask_final=squeeze(mask(:,:,1));
for isource=2:nsource
    mask_final=mask_final.*squeeze(mask(:,:,isource));
end

%% output new ascii model file

filename = sprintf('./mask.dat');
fid=fopen(filename,'w');
for i=1:row	
    fprintf(fid,'%f %f %f %f %f\n',data(i,2),data(i,3),mask_final(i,5),mask_final(i,5),mask_final(i,5));
end
fclose(fid);

