% clear all; close all; clc;
load hop_stat_SFO.mat;

max_hop = 13;
zero_count = zeros(max_hop, 1);
nonzero_count = zeros(max_hop, 1);
zero_count(hop(ASN==-1)) = count(ASN==-1);
for i=1:max_hop
    nonzero_count(i) = sum(count(ASN~=-1 & hop==i));
end
bar(1:max_hop, [zero_count, nonzero_count]);
%%
% filter out ip None data
% clear all; close all; clc;
load hop_stat_SFO.mat;

count = count(ASN~=-1);
hop = hop(ASN~=-1);
ip = ip(ASN~=-1);
ASN = ASN(ASN~=-1);

max_hop = 11;
x = 1:max_hop;
size = sum((hop==max_hop));
y = zeros(size, max_hop);
total_count = zeros(1, max_hop);

for i=1:max_hop
    d_num = length(count(hop==i));
    total_count(i) = d_num;
    step = max(floor(size/d_num), 1);
    y(1:step:d_num*step, i) = count(hop==i);
end

f = subplot(2,1,2);
bar(x, y', 'stack');
ylim([1 max(sum(y, 1))*1.2]);
text(x, sum(y, 1) + 0.01*max(sum(y, 1)), num2str(total_count'),...
     'horiz','center','vert','bottom');
box on;
xlabel('hop #');
ylabel('responding routers');
title('number of routers on each hop');

%# make all text in the figure to size 14 and bold
set(gca,'FontSize',14,'fontWeight','bold')
set(findall(f,'type','text'),'fontSize',16,'fontWeight','bold')
