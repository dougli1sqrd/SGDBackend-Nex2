#! /bin/sh


cd /data/www/SGDBackend-NEX2/current
source /data/envs/sgd/bin/activate 
source dev_variables.sh 
python scripts/loading/reference/reference_update.py
