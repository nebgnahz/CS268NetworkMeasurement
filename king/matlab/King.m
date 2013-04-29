clear all; close all; clc;

load dist_king.mat
[dist, I] = sort(dist_raw);
latency = latency_raw(I);

% filtering
dist = dist(latency<5);
latency = latency(latency<5);

step = 1000;

size = floor(length(dist)/step);

num_bin = floor(max(dist)/step);
x = (1:num_bin).*step;

min_prc = 5;
max_prc = 95;

mean_v = zeros(num_bin, 1);
num_v = zeros(num_bin, 1);
std_v = zeros(num_bin, 2);

for i=1:num_bin
    data = latency(step*i < dist & dist < step*(i+1));
    num_v(i) = length(data);
    % data = latency((i-1)*step+1:i*step);
    mean_v(i) = mean(data);
    std_v(i, :) = prctile(data, [min_prc max_prc]);
end

%%
figure(1);
box on;
f = subplot(2, 1, 1);
h = bar(x, mean_v);
set(h(1),'facecolor','red') % use color name
hold all;
xlabel('distance (km)');
ylabel('latency (second)');

plot(x, x/2/100000, '-gs','LineWidth',2);
xlim([0 20000])
errorbar(x, mean_v, std_v(1:end, 1), std_v(1:end, 2), '.');

%# make all text in the figure to size 14 and bold
set(gca,'FontSize',16,'fontWeight','bold')
set(findall(f,'type','text'),'fontSize',18,'fontWeight','bold')
title('latency vs. distance');

legend('average latency', 'speed-of-light limit');

f = subplot(2, 1, 2);
bar(x, num_v);
xlim([0 20000])
xlabel('distance (km)');
ylabel('count');
title('distribution of distances');

%# make all text in the figure to size 14 and bold
set(gca,'FontSize',16,'fontWeight','bold')
set(findall(f,'type','text'),'fontSize',18,'fontWeight','bold')


% Linear model Poly1:
%      f(x) = p1*x + p2
% Coefficients (with 95% confidence bounds):
%        p1 =   1.798e-05  (1.604e-05, 1.992e-05)
%        p2 =      0.2326  (0.2104, 0.2547)
% 
% Goodness of fit:
%   SSE: 0.008216
%   R-square: 0.9573
%   Adjusted R-square: 0.9548
%   RMSE: 0.02198
