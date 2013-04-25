clear all; close all; clc;

load dist_king.mat
[dist, I] = sort(dist_raw);
latency = latency_raw(I);
step = 1000;

size = floor(length(dist)/step);

num_bin = floor(max(dist)/step);
x = (1:num_bin).*step;

min_prc = 5;
max_prc = 80;

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


figure(1);
box on;
subplot(2, 1, 1)
h = bar(x, mean_v);
set(h(1),'facecolor','red') % use color name
hold all;
plot(x, x/3/100000);
xlim([0 20000])
errorbar(x, mean_v, std_v(1:end, 1), std_v(1:end, 2), '.');
subplot(2, 1, 2)
bar(x, num_v);
xlim([0 20000])


