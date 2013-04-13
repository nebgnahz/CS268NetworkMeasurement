from gQuery import google_scrape, random_string, google_trends
import logging, sys, time

# I might have to rate limit this query
# from someone on stackoverflow, it seems safe to have automatic query with an interval larger than 1 second
# also diverse the search, rather than repeated search a single word


hot_items = google_trends()
random_list = []
for i in range(len(hot_items)):
	query = random_string(32)
	random_list.append(query)

merged_list =  [j for i in zip(hot_items, random_list) for j in i]
reduced_list = merged_list[0:20]

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
sleep_time = 5
repeated_times = 10

# usually the list size is 20, we search each 10 times. then its 200 times
# each time sleep for 5 sec, with additional time spent around 5 sec
# 10 sec * 400 -> 1000 sec -> ~0.5h
# not too bad
# let's test if this will be banned by google

for i in range(repeated_times):
	for item in merged_list:
		# search hot item		
		qTime, gTime, ip, pingTime = google_scrape(item)
		if ip is not None:
			print item, qTime, gTime, ip, pingTime
		time.sleep(sleep_time)
