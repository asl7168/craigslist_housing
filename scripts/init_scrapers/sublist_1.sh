#!/bin/bash
#SBATCH -A p31502               # Allocation
#SBATCH -p long                 # Queue
#SBATCH -t 168:00:00            # Walltime/duration of the job
#SBATCH -N 1                    # Number of Nodes
#SBATCH --mem=1G                # Memory per node in GB needed for a job. Also see --mem-per-cpu
#SBATCH --ntasks-per-node=1     # Number of Cores (Processors)
#SBATCH --output=../outfiles/sublist_1/sublist_1.out    # Path for output must already exist
#SBATCH --error=../outfiles/sublist_1/sublist_1.err     # Path for errors must already exist
#SBATCH --job-name="sublist_1 initial scrape"           # Name of job

/projects/p31502/projects/craigslist/scripts/craig_env_runner

python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("atlanta", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/atlanta_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("denver", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/denver_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("seattle", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/seattle_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("dallas", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/dallas_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("lasvegas", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/lasvegas_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("newyork", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/newyork_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("phoenix", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/phoenix_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("sacramento", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/sacramento_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("baltimore", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/baltimore_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("charlotte", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/charlotte_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("hartford", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/hartford_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("jacksonville", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/jacksonville_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("milwaukee", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/milwaukee_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("newjersey", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/newjersey_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("oklahomacity", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/oklahomacity_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("providence", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/providence_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("sanantonio", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/sanantonio_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("stpetersburg", filepath="../html", proxy="64.189.24.250:3129")' > /projects/p31502/projects/craigslist/scripts/outfiles/stpetersburg_out.out
