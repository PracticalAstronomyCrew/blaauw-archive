#!/usr/bin/env bash

BASE=/home/dachsroot/archive
INS_DIR=$BASE/insert
DONE_DIR=$BASE/done
LOGS=$BASE/logs

# If there is nothing to insert, stop immediately
[[ -z $(ls $INS_DIR) ]] && exit

mkdir -p $INS_DIR
mkdir -p $DONE_DIR
mkdir -p $LOGS

BLAAUW_DIR=/home/dachsroot/blaauw-archive
INSERT_SCRIPT=$BLAAUW_DIR/src/insert.py
COLS=$BLAAUW_DIR/definitions/column-list.csv  # maybe use a different list ?

NOW=$(date +%Y%m%d-%H%M%S)
LOGFILE=$LOGS/insertion-${NOW}.log
touch $LOGFILE

logger () {
        echo $1 &>> $LOGFILE
}

logger "Logfile: $LOGFILE"
logger "Datetime: $NOW"

logger "Starting insertion..."
for file in $(ls $INS_DIR); do 
        logger "--------------------------------------------------------------------------------"
        logger "Inserting file: $file"

        #python3 $INSERT_SCRIPT $INS_DIR/$file $COLS &>> $LOGFILE
        # TODO: Maybe check if the insertion was successful, if not move to another location ??
        status=$?
        logger "Inserting exited with status: $status"
        if [[ $status ]]; then
                logger "WARNING, nonzero exit: $status"
        fi

        mv $INS_DIR/$file $DONE_DIR/$file

        logger "Done with file: $file"
        logger "--------------------------------------------------------------------------------"
done
logger "End of insertion..."

logger "Updating DaCHS VO"
#make --directory=$BLAAUW_DIR reload-rd publish-rd &>> $LOGFILE
logger "Done Updating DaCHS VO"
