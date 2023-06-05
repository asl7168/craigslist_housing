#!/bin/bash
#SBATCH -A p31502                                           # Allocation
#SBATCH -p gengpu                                           # Queue
#SBATCH --gres=gpu:a100:1 
#SBATCH -N 1                                                # Number of nodes
#SBATCH -n 1                                                # Number of cores (processors)
#SBATCH -t 48:00:00                                         # Walltime/duration of job
#SBATCH --mem=16G                                           # Memory per node in GB needed for a job. Also see --mem-per-cpu
#SBATCH --output=./outfiles/distilroberta/seattle_train.out # Path for output must already exist
#SBATCH --error=./outfiles/distilroberta/seattle_train.err  # Path for error must already exist
#SBATCH --job-name="distilling seattle"

module purge
cd /projects/p31502/projects/craigslist
source activate ./venv_craig_env/bin/activate
cd ./models/distilroberta
python distilroberta.py seattle
