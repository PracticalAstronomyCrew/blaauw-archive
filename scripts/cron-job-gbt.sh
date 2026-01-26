#!/bin/bash

# Python version 3.8 is located here
PATH=/opt/dachs/bin:$PATH

DATA_DIR=$HOME/cronjob-data
BLAAUW_DIR=$HOME/blaauw-archive
LOG_DIR=$HOME/cronjob-logs

NOW=$(date +%Y%m%d-%H%M%S)

YESTERDAY=$(date -d "`date`-1days" +%F) # YYYY-MM-DD

GBT_FILE=$DATA_DIR/${YESTERDAY}-raw-headers.GBT.pickle

LOG_FILE=$LOG_DIR/${NOW}-cronjob-gbt.log

echo "Crawling..." > $LOG_FILE
python3 $BLAAUW_DIR/scripts/crawler.py --output $DATA_DIR --date $YESTERDAY --base GBT &>> $LOG_FILE

echo "Inserting" >> $LOG_FILE
python3 $BLAAUW_DIR/scripts/insert.py --file $GBT_FILE &>> $LOG_FILE

echo "Removing" >> $LOG_FILE
rm $GBT_FILE
