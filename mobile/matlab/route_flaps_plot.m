%% clear all; close all; clc;
load route_flaps_data.mat;

hop_max = 13;
x=1:hop_max;
mean_v = zeros(hop_max, 1);
std_v = zeros(hop_max, 2);
flap_data = zeros(hop_max, 3);

for i=1:hop_max
    data = eval(genvarname(['d' sprintf('%d',i)]));
    % data = latency((i-1)*step+1:i*step);
    flap_data(i, :) = hist(data, [1,2,3]);
end

f = bar(x, flap_data, 'stack');
legend('1', '2', '3')
axis([0 hop_max+1 0 4500])
xlabel('hop #');
ylabel('number of routes');
title('routing flaps');

%# make all text in the figure to size 14 and bold
set(gca,'FontSize',14,'fontWeight','bold')
set(findall(f,'type','text'),'fontSize',16,'fontWeight','bold')
