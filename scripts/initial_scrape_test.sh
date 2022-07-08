#!/bin/bash
#SBATCH -A e31408               # Allocation
#SBATCH -p normal                # Queue
#SBATCH -t 12:00:00             # Walltime/duration of the job
#SBATCH -N 1                    # Number of Nodes
#SBATCH --mem=18G               # Memory per node in GB needed for a job. Also see --mem-per-cpu
#SBATCH --ntasks-per-node=6     # Number of Cores (Processors)
#SBATCH --output=../outs_and_errs/politifact_out.out    # Path for output must already exist
#SBATCH --error=../outs_and_errs/politifact_err.err     # Path for errors must already exist
#SBATCH --job-name="pants on fire"       # Name of job

/projects/p31502/projects/craigslist/scripts/craig_env_runner 

python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_initial_scrape("atlanta", filepath="../html")' > /projects/p31502/projects/craigslist/scripts/outfiles/atlanta_out.out
