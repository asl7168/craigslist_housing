#!/bin/bash
#SBATCH -A p31502               # Allocation
#SBATCH -p normal               # Queue
#SBATCH -t 20:00:00             # Walltime/duration of the job
#SBATCH -N 1                    # Number of Nodes
#SBATCH --mem=1G                # Memory per node in GB needed for a job. Also see --mem-per-cpu
#SBATCH --ntasks-per-node=1     # Number of Cores (Processors)
#SBATCH --output=../outfiles/sanantonio/sanantonio.out    # Path for output must already exist
#SBATCH --error=../outfiles/sanantonio/sanantonio.err     # Path for errors must already exist
#SBATCH --job-name="initial sanantonio scrape"       # Name of job

/projects/p31502/projects/craigslist/scripts/craig_env_runner

python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_initial_scrape("sanantonio", filepath="../../html")'
