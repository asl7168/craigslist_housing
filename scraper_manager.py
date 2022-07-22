from proxy_manager import reverify_proxies
from state_codes import state_codes
import os
from math import floor, ceil
import json

header = "#!/bin/bash\n#SBATCH -A p31502               # Allocation\n#SBATCH -p long                 # Queue\n\
#SBATCH -t 168:00:00            # Walltime/duration of the job\n#SBATCH -N 1                    # Number of Nodes\n\
#SBATCH --mem=1G                # Memory per node in GB needed for a job. Also see --mem-per-cpu\n\
#SBATCH --ntasks-per-node=1     # Number of Cores (Processors)\n"

def setup(init: bool=False):
    init_or_cron = "init" if init else "cron"
    initcron_dir = f"./scripts/{init_or_cron}_scrapers"
    [os.remove(os.path.join(initcron_dir, f)) for f in os.listdir(initcron_dir)]  # clear appropriate dir out
    
    # f = open("proxies/reverified_proxies.json")
    # proxies = json.load(f)
    proxies = reverify_proxies()  # reverify proxies, then store them here
    f.close()
    locations = ["chicago", "atlanta", "boston", "cleveland", "denver", "losangeles", "memphis", "seattle", 
                "sfbay", "austin", "dallas", "detroit", "houston", "lasvegas", "miami", "minneapolis", 
                "newyork", "orangecounty", "philadelphia", "phoenix", "portland", "raleigh", "sacramento", 
                "sandiego", "washingtondc"]  # ordered by priority

    [locations.append(l) for l in list(state_codes.keys()) if l not in locations]  # add non-priority locations

    n = len(proxies)  # the number of available proxies, i.e. how many scrapings can be done at once

    sublists = [[] for _ in range(n)]  # create n sublists to divide locations into
    [sublists[i].extend(locations[i::n]) for i in range(n)]  # maintain priority by picking every n location
    
    # print(len(locations) == len([i for sublist in sublists for i in sublist]))
    

    def generate_scripts(subs: sublists, from_keyed: bool = False):
        if from_keyed: r = list(subs.keys())
        else: r = range(len(subs))
        for i in r:
            name = f"sublist_{i}"

            if not os.path.exists(f"./scripts/outfiles/{name}"): os.mkdir(f"./scripts/outfiles/{name}")

            output = header + f'#SBATCH --output=../outfiles/{name}/{name}.out    # Path for output must already exist\n' + \
                     f'#SBATCH --error=../outfiles/{name}/{name}.err     # Path for errors must already exist\n' + \
                     f'#SBATCH --job-name="{name} initial scrape"           # Name of job\n\n' + \
                     "/projects/p31502/projects/craigslist/scripts/craig_env_runner\n\n"

            for loc in subs[i]:
                output += f"python -c 'import sys; sys.path.append(\"/projects/p31502/projects/craigslist/\"); " + \
                f"from cronable_scraping import *; do_{init_or_cron}_scrape(\"{loc}\", filepath=\"../html\", proxy=" + \
                f"\"{proxies[i] if not from_keyed else proxies[floor(i)]}\")' " + \
                f"> /projects/p31502/projects/craigslist/scripts/outfiles/{loc}/{loc}_out.out\n"

            if from_keyed:
                if i is not list(filter(lambda x: x >= floor(i) and x < floor(i)+1, r))[-1]:  # if not the last key between i and i+1, need to queue next
                    output += f"\nsbatch /projects/p31502/projects/craigslist/{initcron_dir[2:]}/sublist_{str(floor(i))+'.'+str(i+0.1).split('.')[1][0]}.sh"

            with open(f"{initcron_dir}/{name}.sh", "w") as outfile:
                outfile.write(output)

    # max QUEST job length is 168 hours, and each init scrape takes up to 16 hours, so we can only run 10 init scrapes per job
    if not len(locations) / n <= 10:
        keyed_sublists = dict()
        for i in range(n):
            segmented_sublist = [sublists[i][j:j+10] for j in range(0, len(sublists[i]), 10)]
            for j in range(len(segmented_sublist)):
                keyed_sublists[float(f"{i}.{j}")] = segmented_sublist[j]
        
        generate_scripts(keyed_sublists, True)
    else:
        generate_scripts()
