#!/bin/bash
LOG="/var/log/cron.log";
FOLDER="/home/ucb_268_measure/CS268NetworkMeasurement/DC/"
FILE="controller.py"
echo "Start_of_Schedule" >> $LOG;
date >> $LOG;
/usr/bin/python $FOLDER$FILE >> $LOG;
date >> $LOG;
echo "End_of_Schedule" >> $LOG;

