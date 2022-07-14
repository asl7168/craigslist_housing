#!/bin/bash
#SBATCH -A p31502               # Allocation
#SBATCH -p long                 # Queue
#SBATCH -t 168:00:00            # Walltime/duration of the job
#SBATCH -N 1                    # Number of Nodes
#SBATCH --mem=1G                # Memory per node in GB needed for a job. Also see --mem-per-cpu
#SBATCH --ntasks-per-node=1     # Number of Cores (Processors)
#SBATCH --output=../outfiles/topcities/topcities.out    # Path for output must already exist
#SBATCH --error=../outfiles/topcities/topcities.err     # Path for errors must already exist
#SBATCH --job-name="top cities initial scrape"       # Name of job

/projects/p31502/projects/craigslist/scripts/craig_env_runner

python top_cities_init_scrape.py
