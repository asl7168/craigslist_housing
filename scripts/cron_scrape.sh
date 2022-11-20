#!/bin/bash

source /projects/p31502/projects/craigslist/venv_craig_env/bin/activate
python /projects/p31502/projects/craigslist/scripts/cron_scrape.py 1> /projects/p31502/projects/craigslist/scripts/outfiles/cron_scrape.out 2> /projects/p31502/projects/craigslist/scripts/outfiles/cron_scrape.err
deactivate
