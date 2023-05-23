#!/bin/bash
#SBATCH --account=p31502 ## Required: your allocation/account name, i.e. eXXXX, pXXXX or bXXXX
#SBATCH --partition=short ## Required: (buyin, short, normal, long, gengpu, genhimem, etc)
#SBATCH --array=0
#SBATCH --time=2:00:00 ## Required: How long will the job need to run (remember different partitions have restrictions on this parameter)
#SBATCH --nodes=1 ## how many computers/nodes do you need (no default)
#SBATCH --ntasks-per-node=1 ## how many cpus or processors do you need on per computer/node (default value 1)
#SBATCH --mem=15G ## how much RAM do you need per computer/node (this affects your FairShare score so be careful to not ask for more than you need))
#SBATCH --job-name="csv_processing_${SLURM_ARRAY_TASK_ID}" ## When you run squeue -u  this is how you can identify the job
#SBATCH --output=/projects/p31502/projects/craigslist/scripts/outfiles/csv_process_%A_%a.txt ## standard out and standard error goes to this file


module purge all
module load python-anaconda3
source activate /projects/p31502/projects/craigslist/craig_env

IFS=$'\n' read -d '' -r -a metro_areas < metro_areas.txt

python /projects/p31502/projects/craigslist/scripts/process_files.py --metro_area ${metro_areas[$SLURM_ARRAY_TASK_ID]}

 