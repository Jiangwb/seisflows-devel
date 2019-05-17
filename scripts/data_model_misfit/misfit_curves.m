clc;clear;close all;
%% Data&Model misfit curves
iter=1:20;

vp_misfit=load('./vp_misfit');
vs_misfit=load('./vs_misfit');

data_misfit=load('../output.stats/misfit');

%%
figure(1);
plot(iter,data_misfit,'-*','color','black','linewidth',2);hold on;
set(gcf,'unit','centimeters','position',[0 0 15 12]);
set(gca,'FontSize',16);
set(gca,'XAxisLocation','bottom','YAxisLocation','left');
%axis([1 10 0.4 1]);hold on
set(gca,'Xtick',[0 5 10 15 20]);
set(gca,'XTickLabel',{'0','5','10','15','20'});
xlabel('Iteration Number','fontsize',18);
ylabel('Normalized waveform misfit','fontsize',18);

figure(2);
plot(iter,vp_misfit,'-v','color','black','linewidth',2);hold on;
set(gcf,'unit','centimeters','position',[0 0 15 12]);
set(gca,'FontSize',16);
set(gca,'XAxisLocation','bottom','YAxisLocation','left');
%axis([1 20 1.0 1.7]);hold on
set(gca,'Xtick',[0 5 10 15 20]);
set(gca,'XTickLabel',{'0','5','10','15','20'});
xlabel('Iteration Number','fontsize',18);
ylabel('Vp model misfit (m/s)','fontsize',18);

figure(3);
plot(iter,vs_misfit,'-v','color','black','linewidth',2);hold on;
set(gcf,'unit','centimeters','position',[0 0 15 12]);
set(gca,'FontSize',16);
set(gca,'XAxisLocation','bottom','YAxisLocation','left');
%axis([1 20 1.0 1.7]);hold on
set(gca,'Xtick',[0 5 10 15 20]);
set(gca,'XTickLabel',{'0','5','10','15','20'});
xlabel('Iteration Number','fontsize',18);
ylabel('Vs model misfit (m/s)','fontsize',18);