#!/bin/bash


DATA_DIR=$HOME/cronjob-data
BLAAUW_DIR=$HOME/blaauw-archive

# NOW=$(date +%Y%m%d-%H%M%S)

LAST_MONTH=$(date -d "`date`-30days" +%F) # YYYY-MM-DD
TODAY=$(date +%F) # YYYY-MM-DD

LDST_FILE=$DATA_DIR/${YESTERDAY}-raw-headers.LDST.pickle

echo "Crawling..."
python3 $BLAAUW_DIR/scripts/crawler.py --output $DATA_DIR --from-date $LAST_MONTH --to-date $TODAY --base LDST

echo "Inserting"
python3 $BLAAUW_DIR/scripts/insert.py --file $LDST_FILE

echo "Removing"
rm $LDST_FILE
