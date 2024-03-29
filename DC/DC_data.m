%%
close all; clear all; clc;
f = ls('../CS268Data/gQuery*.csv');
r = regexp(f,'\n','split');

total_file = length(r)-1;
bar_data = zeros(1, total_file);
min_prc = 5;
max_prc = 95;
x = 1:total_file;

mean_r_v = zeros(total_file, 1);
std_r_v = zeros(total_file, 2);
mean_h_v = zeros(total_file, 1);
std_h_v = zeros(total_file, 2);
mean_p_v = zeros(total_file, 1);
std_p_v = zeros(total_file, 2);
mean_g_v = zeros(total_file, 1);
std_g_v = zeros(total_file, 2);

mean_gP_v = zeros(total_file, 1);
std_gP_v = zeros(total_file, 2);

for i=1:total_file
    tmp = r(i);
    [query,index,ip,qTime,gTime,pTime, bRandom] = importfun(tmp{1});
    
    new_p_time = pTime( pTime~=-1);
    
    random_data = qTime(pTime~=-1 & bRandom==1 & index==1);
    hottrend_data = qTime(pTime~=-1 & bRandom==0 & index~=1);
    google_data = gTime(pTime~=-1 & bRandom==0 & index~=1);
    
    mean_r_v(i) = prctile(random_data, 50);
    std_r_v(i, :) = prctile(random_data, [min_prc max_prc]);
    
    mean_h_v(i) = prctile(hottrend_data, 50);
    std_h_v(i, :) = prctile(hottrend_data, [min_prc max_prc]);
    
    mean_g_v(i) = prctile(google_data, 50);
    std_g_v(i, :) = prctile(google_data, [min_prc max_prc]);

    mean_p_v(i) = prctile(new_p_time, 50);
    std_p_v(i, :) = prctile(new_p_time, [min_prc max_prc]);
    
    % fprintf('%4.2f\n', min(qTime));
    % fprintf(max(qTime));
    
    gPortion_data = google_data(google_data ~= -1)./hottrend_data(google_data ~= -1);
    mean_gP_v(i) = mean(gPortion_data);
    std_gP_v(i, :) = prctile(gPortion_data, [min_prc max_prc]);
    
end

%%
hold on;
box on;

h = barh(x, mean_gP_v);
% text(x, 250*ones(1, length(x)), num2str(mean_r_v, '%2.2f'),...
%       'horiz','center','vert','bottom');
set(h(1),'facecolor','red') % use color name
hold all;

herrorbar(mean_gP_v, x', std_gP_v(1:end, 1)-mean_gP_v, std_gP_v(1:end, 2)-mean_gP_v);

set(gca, 'YTick', [1:19], ...
       'YTickLabel',{'epfl.ch',...
                     'ucl.ac.be',...
                     '6test.edu.cn',...
                     'ics.tut.ac.jp',...
                     'uba.ar',...
                     'ijs.si',...
                     'cmu.edu',...
                     'ait.ie',...
                     'tu-berlin.de',...
                     'ucla.edu',...
                     'uoregon.edu',...
                     'ei.tum.de',...
                     'cam.ac.uk',...
                     'uzh.ch',...
                     'iitkgp.ac.in',...
                     'ionio.gr',...
                     'wisc.edu',...
                     'univie.ac.at',...
                     'singaren.net.sg',...
                     });
                 
%# make all text in the figure to size 14 and bold
set(gca,'FontSize',14,'fontWeight','bold')
set(findall(h,'type','text'),'fontSize',16,'fontWeight','bold')


%%
close all;
hold on;
f = barh(x, [mean_r_v, mean_h_v, mean_g_v, mean_p_v./1000], 'grouped');
set(gca, 'YTick', [1:19], ...
       'YTickLabel',{'epfl.ch',...
                     'ucl.ac.be',...
                     '6test.edu.cn',...
                     'ics.tut.ac.jp',...
                     'uba.ar',...
                     'ijs.si',...
                     'cmu.edu',...
                     'ait.ie',...
                     'tu-berlin.de',...
                     'ucla.edu',...
                     'uoregon.edu',...
                     'ei.tum.de',...
                     'cam.ac.uk',...
                     'uzh.ch',...
                     'iitkgp.ac.in',...
                     'ionio.gr',...
                     'wisc.edu',...
                     'univie.ac.at',...
                     'singaren.net.sg',...
                     });

legend('random query', 'hot trends', 'google time', 'ping time');
% errorbar(x+0.15, mean_h_v, std_h_v(1:end, 1), std_h_v(1:end, 2), '.');
% errorbar(x-0.15, mean_r_v, std_r_v(1:end, 1), std_r_v(1:end, 2), '.');
box on;
%# make all text in the figure to size 14 and bold
set(gca,'FontSize',14,'fontWeight','bold')
set(findall(f,'type','text'),'fontSize',20,'fontWeight','bold')




%% 
% bar web like drawing

data = [mean_r_v, mean_h_v, mean_g_v, mean_p_v./1000];
std_v = [std_r_v, std_h_v, std_g_v, std_p_v./1000];
h = bar(data);
set(h,'BarWidth',1); % The bars will now touch each other

set(gca,'YGrid','on')
% set(gca,'GridLineStyle','-')
set(gca,'XTicklabel','EECS-Secure|iPhone');
ylabel('Latency')

lh = legend('random query','hot trends', 'google time', 'ping time');
% set(lh,'Location','BestOutside','Orientation','horizontal')

hold on;

numgroups = size(data, 1); 
numbars = size(data, 2); 

groupwidth = min(0.8, numbars/(numbars+1.5));

for i = 1:numbars
% Based on barweb.m by Bolu Ajiboye from MATLAB File Exchange
x = (1:numgroups) - groupwidth/2 + (2*i-1) * groupwidth / (2*numbars); % Aligning error bar with individual bar
errorbar(x, data(:, i), std_v(:, 2*i-1)-data(:, i), std_v(:, 2*i)-data(:, i), ...
        '-b', 'LineWidth', 1.2, 'MarkerEdgeColor','k', 'linestyle', 'none');
end

%# make all text in the figure to size 14 and bold
set(gca,'FontSize',16,'fontWeight','bold')
set(findall(h,'type','text'),'fontSize',18,'fontWeight','bold')
