#! /bin/sh

cd /data/www/SGDBackend-NEX2/current
source /data/envs/sgd/bin/activate && source prod_variables.sh && CREATED_BY=fgondwe python scripts/loading/files/load_filedbentities.py
