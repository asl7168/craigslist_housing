#!/bin/bash
#SBATCH -A p31502               # Allocation
#SBATCH -p long                 # Queue
#SBATCH -t 168:00:00            # Walltime/duration of the job
#SBATCH -N 1                    # Number of Nodes
#SBATCH --mem=1G                # Memory per node in GB needed for a job. Also see --mem-per-cpu
#SBATCH --ntasks-per-node=1     # Number of Cores (Processors)
#SBATCH --output=../outfiles/sublist_0/sublist_0.out    # Path for output must already exist
#SBATCH --error=../outfiles/sublist_0/sublist_0.err     # Path for errors must already exist
#SBATCH --job-name="sublist_0 initial scrape"           # Name of job

/projects/p31502/projects/craigslist/scripts/craig_env_runner

python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("chicago", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/chicago_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("cleveland", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/cleveland_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("memphis", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/memphis_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("austin", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/austin_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("houston", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/houston_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("minneapolis", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/minneapolis_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("philadelphia", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/philadelphia_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("raleigh", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/raleigh_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("washingtondc", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/washingtondc_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("buffalo", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/buffalo_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("columbus", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/columbus_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("inlandempire", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/inlandempire_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("louisville", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/louisville_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("nashville", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/nashville_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("norfolk", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/norfolk_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("pittsburgh", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/pittsburgh_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("saltlakecity", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/saltlakecity_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("stlouis", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/stlouis_out.out
python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_init_scrape("watertown", filepath="../html", proxy="157.100.12.138:999")' > /projects/p31502/projects/craigslist/scripts/outfiles/watertown_out.out
