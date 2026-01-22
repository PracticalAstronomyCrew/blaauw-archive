#!/bin/bash


DATA_DIR=$HOME/cronjob-data
BLAAUW_DIR=$HOME/blaauw-archive

# NOW=$(date +%Y%m%d-%H%M%S)

YESTERDAY=$(date -d "`date`-2days" +%F) # YYYY-MM-DD

GBT_FILE=$DATA_DIR/${YESTERDAY}-raw-headers.GBT.pickle

echo "Crawling..."
python3 $BLAAUW_DIR/scripts/crawler.py --output $DATA_DIR --date $YESTERDAY --base GBT

echo "Inserting"
python3 $BLAAUW_DIR/scripts/insert.py --file $GBT_FILE

echo "Removing"
rm $GBT_FILE

# python3 $BLAAUW_DIR/scripts/crawler.py --output data/ --from-date 250101 --to-date 260101 --base GBT
# LDST
