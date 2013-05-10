%%
load delay_hop.mat;

hop_max = 11;
min_prc = 5;
max_prc = 95;
prc = [5 95 99];

x=1:hop_max;
mean_v = zeros(hop_max, 1);
std_v = zeros(hop_max, 3);
for i=1:hop_max
    data = eval(genvarname(['d' sprintf('%d',i)]));
    % data = latency((i-1)*step+1:i*step);
    mean_v(i) = mean(data);
    std_v(i, :) = prctile(data, prc);
end

hold on;
box on;
f = subplot(2, 1, 1);
h = bar(x, mean_v);
% t = text(x, mean_v' + 0.01*max(mean_v'), num2str(mean_v, '%2.2f'),...
%      'horiz','center','vert','bottom', 'BackgroundColor',[.7 .9 .7]);
text(x, 170*ones(1, length(x)), num2str(mean_v, '%2.2f'),...
      'horiz','center','vert','bottom');
set(h(1),'facecolor','red') % use color name
hold all;

% str = num2str(mean_v, '%2.2f');
% concat = char(10)*ones(max_hop,1);
% index = num2str((1:max_hop)', '%d');
% 
% set(f,'XTickLabel', [index concat str])

% plot(x, std_v(1:end, 1), '-bv',...
%      x, std_v(1:end, 2), '-rs', ...
%      x, std_v(1:end, 3), '-g*',...
%      'LineWidth', 2,...
%      'MarkerSize',10);

errorbar(x, mean_v, std_v(1:end, 1)-mean_v, std_v(1:end, 2)-mean_v, '.');
xlabel('hop #');
ylabel('latency statistics');
title('latency using traceroute');

%# make all text in the figure
set(gca,'FontSize',16)
set(get(gca,'XLabel'),'FontSize',18); 
set(get(gca,'YLabel'),'FontSize',18);
set(get(gca,'Title'),'FontSize',18);
set(findall(f,'type','text'),'fontSize',18)


%%
load delay_hop_SFO.mat;

hop_max = 11;
min_prc = 5;
max_prc = 95;
x=1:hop_max;
mean_v = zeros(hop_max, 1);
std_v = zeros(hop_max, 2);
for i=1:hop_max
    data = eval(genvarname(['d' sprintf('%d',i)]));
    % data = latency((i-1)*step+1:i*step);
    mean_v(i) = mean(data);
    std_v(i, :) = prctile(data, [min_prc max_prc]);
end

hold on;
box on;
f = subplot(2, 1, 1);
h = bar(x, mean_v);
% t = text(x, mean_v' + 0.01*max(mean_v'), num2str(mean_v, '%2.2f'),...
%      'horiz','center','vert','bottom', 'BackgroundColor',[.7 .9 .7]);
text(x, 450*ones(1, length(x)), num2str(mean_v, '%2.2f'),...
      'horiz','center','vert','bottom');
set(h(1),'facecolor','red') % use color name
hold all;

% str = num2str(mean_v, '%2.2f');
% concat = char(10)*ones(max_hop,1);
% index = num2str((1:max_hop)', '%d');
% 
% set(f,'XTickLabel', [index concat str])

errorbar(x, mean_v, std_v(1:end, 1)-mean_v, std_v(1:end, 2)-mean_v, '.');
xlabel('hop #');
ylabel('latency statistics');
title('latency using traceroute');

%# make all text in the figure
set(gca,'FontSize',16)
set(get(gca,'XLabel'),'FontSize',18); 
set(get(gca,'YLabel'),'FontSize',18);
set(get(gca,'Title'),'FontSize',18);
set(findall(f,'type','text'),'fontSize',18)

