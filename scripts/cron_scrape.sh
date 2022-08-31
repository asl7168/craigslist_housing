#!/bin/bash

source /projects/p31502/projects/craigslist/venv_craig_env/bin/activate
python /projects/p31502/projects/craigslist/scripts/cron_scrape.py 1> /projects/p31502/projects/craigslist/scripts/outfiles/cron_scrape.out 2> /projects/p31502/projects/craigslist/scripts/outfiles/cron_scrape.err
deactivate

conda activate /projects/p31502/projects/craigslist/craig_env 
python /projects/p31502/projects/craigslist/scripts/process_files.py 1> /projects/p31502/projects/craigslist/scripts/outfiles/process_files.out 2> /projects/p31502/projects/craigslist/scripts/outfiles/process_files.err 
conda deactivate