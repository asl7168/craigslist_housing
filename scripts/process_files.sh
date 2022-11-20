#!/bin/bash

conda activate /projects/p31502/projects/craigslist/craig_env
python /projects/p31502/projects/craigslist/scripts/process_files.py 1> /projects/p31502/projects/craigslist/scripts/outfiles/process_files.out 2> /projects/p31502/projects/craigslist/scripts/outfiles/process_files.err 
conda deactivate
