#!/bin/bash
#SBATCH -A p31502               # Allocation
#SBATCH -p long                 # Queue
#SBATCH -t 168:00:00            # Walltime/duration of the job
#SBATCH -N 1                    # Number of Nodes
#SBATCH --mem=1G                # Memory per node in GB needed for a job. Also see --mem-per-cpu
#SBATCH --ntasks-per-node=1     # Number of Cores (Processors)
#SBATCH --output=../outfiles/sublist_2/sublist_2.out    # Path for output must already exist
#SBATCH --error=../outfiles/sublist_2/sublist_2.err     # Path for errors must already exist
#SBATCH --job-name="sublist_2 initial scrape"           # Name of job

/projects/p31502/projects/craigslist/scripts/craig_env_runner

python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("boston", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/boston_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("losangeles", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/losangeles_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("sfbay", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/sfbay_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("detroit", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/detroit_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("miami", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/miami_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("orangecounty", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/orangecounty_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("portland", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/portland_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("sandiego", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/sandiego_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("bham", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/bham_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("cincinnati", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/cincinnati_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("indianapolis", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/indianapolis_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("kansascity", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/kansascity_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("muncie", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/muncie_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("niagara", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/niagara_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("orlando", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/orlando_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("richmond", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/richmond_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("sanmarcos", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/sanmarcos_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("tampa", filepath="../html", proxy="46.53.191.60:3128")' > /projects/p31502/projects/craigslist/scripts/outfiles/tampa_out.out
