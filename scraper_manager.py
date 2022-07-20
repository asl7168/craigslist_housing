from proxy_manager import reverify_proxies
from state_codes import state_codes
import os

header = "#!/bin/bash\n#SBATCH -A p31502               # Allocation\n#SBATCH -p long                 # Queue\n\
#SBATCH -t 168:00:00            # Walltime/duration of the job\n#SBATCH -N 1                    # Number of Nodes\n\
#SBATCH --mem=1G                # Memory per node in GB needed for a job. Also see --mem-per-cpu\n\
#SBATCH --ntasks-per-node=1     # Number of Cores (Processors)\n"

def setup(init: bool=False):
    init_or_cron = "init" if init else "cron"
    initcron_dir = f"./scripts/{init_or_cron}_scrapers"
    [os.remove(os.path.join(initcron_dir, f)) for f in os.listdir(initcron_dir)]  # clear appropriate dir out
    
    proxies = reverify_proxies()  # reverify proxies, then store them here
    locations = ["chicago", "atlanta", "boston", "cleveland", "denver", "losangeles", "memphis", "seattle", 
                "sfbay", "austin", "dallas", "detroit", "houston", "lasvegas", "miami", "minneapolis", 
                "newyork", "orangecounty", "philadelphia", "phoenix", "portland", "raleigh", "sacramento", 
                "sandiego", "washingtondc"]  # ordered by priority

    [locations.append(l) for l in list(state_codes.keys()) if l not in locations]  # add non-priority locations

    n = len(proxies)  # the number of available proxies, i.e. how many scrapings can be done at once

    sublists = [[] for _ in range(n)]  # create n sublists to divide locations into
    [sublists[i].extend(locations[i::n]) for i in range(n)]  # maintain priority by picking every n location
    
    # print(len(locations) == len([i for sublist in sublists for i in sublist]))
    
    for i in range(len(sublists)):
        name = f"sublist_{i}"
        output = header + f'#SBATCH --output=../outfiles/{name}/{name}.out    # Path for output must already exist\n' + \
                 f'#SBATCH --error=../outfiles/{name}/{name}.err     # Path for errors must already exist\n' + \
                 f'#SBATCH --job-name="{name} initial scrape"           # Name of job\n\n' + \
                 "/projects/p31502/projects/craigslist/scripts/craig_env_runner\n\n"

        for loc in sublists[i]:
            output += f"python -c 'import sys; sys.path.append(\"/projects/p31502/projects/craigslist/\"); " + \
            f"from cronable_scraping import *; do_{init_or_cron}_scrape(\"{loc}\", filepath=\"../html\", proxy=\"{proxies[i]}\")' " + \
            f"> /projects/p31502/projects/craigslist/scripts/outfiles/{loc}/{loc}_out.out\n"

        with open(f"{initcron_dir}/{name}.sh", "w") as outfile:
            outfile.write(output)

        if not os.path.exists(f"./scripts/outfiles/{name}"): os.mkdir(f"./scripts/outfiles/{name}")
