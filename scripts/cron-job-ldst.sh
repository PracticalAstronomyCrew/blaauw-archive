#!/bin/bash


DATA_DIR=$HOME/cronjob-data
BLAAUW_DIR=$HOME/blaauw-archive

# NOW=$(date +%Y%m%d-%H%M%S)

LAST_MONTH=$(date -d "`date`-30days" +%F) # YYYY-MM-DD
TODAY=$(date +%F) # YYYY-MM-DD

LDST_FILE=$DATA_DIR/${LAST_MONTH}-${TODAY}-raw-headers.LDST.pickle

LOG_FILE=$LOG_DIR/${NOW}-cronjob-ldst.log

echo "Crawling..." > $LOG_FILE
python3 $BLAAUW_DIR/scripts/crawler.py --output $DATA_DIR --from-date $LAST_MONTH --to-date $TODAY --base LDST &>> $LOG_FILE

echo "Inserting" >> $LOG_FILE
python3 $BLAAUW_DIR/scripts/insert.py --file $LDST_FILE &>> $LOG_FILE

echo "Removing" >> $LOG_FILE
rm $LDST_FILE
