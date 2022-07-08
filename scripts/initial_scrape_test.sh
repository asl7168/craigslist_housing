/projects/p31502/projects/craigslist/scripts/craig_env_runner 

python -c 'import sys; sys.path.append("/projects/p31502/projects/craigslist/"); from cronable_scraping import *; do_initial_scrape("atlanta", filepath="../html")' > /projects/p31502/projects/craigslist/scripts/outfiles/atlanta_out.out &
