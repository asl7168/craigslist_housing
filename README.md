# Northwestern Linguistics Mechanisms Lab -- Craigslist Housing Analysis

## Table of Contents
* [Getting Started](#getting-started) 
    * [Working on QUEST](#working-on-quest)
* [Scraping](#scraping)
    * [Proxies](#proxies)
    * [Scraping Python Files](#python-files)
    * [Making a Cronjob](#making-a-cronjob)
* [File Processing](#file-processing)
    * [Processing Python Files](#python-files-1)
    * [R Files](#r-files)

---

## Getting Started
This project relies on the following dependencies:
* Python 3.9.x
* beautifulsoup4 == 4.11.1
* c-print == 1.0.1
* en-core-web-sm
* geopandas
* lxml == 4.9.1
* pandas == 1.4.3
* spacy == 3.4.1
* tqdm == 4.64.0

Other version of these packages may work correctly, but these are the specific ones we're using. `en-core-web-sm` is missing a version number since it varies based on the machine (Windows, QUEST RedHat), and `geopandas` is using a conda temp build.

The majority of the above packages (excluding `geopandas`) can be pip installed from the [venv_requirements.txt](./requirements_and_env_files/venv_requirements.txt) file.

Otherwise, you can create a conda environment from the [conda_craig_env.yaml](./requirements_and_env_files/conda_craig_env.yaml) and [r-stm.yaml](./requirements_and_env_files/r-stm.yaml) files.

***WARNING: both conda requirement files were created on a Northwestern QUEST user node -- as such, there may be issues when installing to another filesystem (e.g. Windows). It may be easier to install packages manually rather than using these files.***

### Working on QUEST
Preexisting venv and conda environments exist within the p31502 allocation on Northwestern QUEST. The environment activation commands below assume you have navigated to the craigslist directory (/projects/p31502/projects/craigslist): 

venv:
```bash
source ./venv_craig_env/bin/activate
```

conda:
```bash
conda activate ./craig_env
```

If you don't have access to the allocation, both venvs and conda envs can be created as usual.

---

## Scraping

### Proxies
The proxies that we're using to scrape with have been purchased from webshare.io. If you're working on QUEST, a webshare_proxies.txt file and a webshare_credentials.py file should already be included in the craigslist project folder. However, if you're sourcing your own proxies from webshare.io, you'll need to download your proxy list and save it into [proxies/webshare_proxies.txt](proxies/webshare_proxies.txt) (if aren't using the rotating proxy link; see [cronable_scraping.py](./cronable_scraping.py)) -- each can be cleaned and tested using the functions in [proxy_manager.py](./proxy_manager.py) 

Additionally, you'll need to create a webshare_credentials.py file in the main project folder of the form:

```python
user = # username listed in https://proxy.webshare.io/proxy/list?
password = # password listed in https://proxy.webshare.io/proxy/list?
```

These can be set in your [proxy settings](https://proxy.webshare.io/proxy/settings?); we additionally recommend changing your Proxy Session Timeout to the maximum, 168 hours, to prevent frequent redownloading of the proxy list.

### Python Files
For more information about the functions included in [cronable_scraping.py](./cronable_scraping.py), [proxy_manager.py](./proxy_manager.py), and [scraper_manager.py](./scraper_manager.py), please read their docstrings and comments.

### Making a Cronjob
1. Run `setup()` from [scraper_manager.py](./scraper_manager.py) with the appropriate flags (at a minimum, not init=True)
2. Edit your crontab file with `crontab -e`
3. Set the frequency to daily (anything of the form `X X * * *`)
4. Enter the command(s) to execute

The full command we're running on QUEST is:
```bash
10 0 * * * source /projects/p31502/projects/craigslist/venv_craig_env/bin/activate; python /projects/p31502/projects/craigslist/scripts/cron_scrape.py 1> /projects/p31502/projects/craigslist/scripts/outfiles/cron_scrape.out 2> /projects/p31502/projects/craigslist/scripts/outfiles/cron_scrape.err; deactivate
```

---

## File Processing
There are multiple steps to processing the scraped HTML files from Craigslist. First, the important information is extracted from each HTML file for each city and added to a file called {location}_complete.csv using functions from [text_processing.py](./text_processing.py) -- if the post is a duplicate, it's ignored; and if it's a repost, the repost date is added to the previous row containing its data (but the data itself isn't duplicated). Then, demographic data is appended to each _complete CSV using functions from [secondary_processing.py](./secondary_processing.py). Finally, plots/models/figures are generated using [stm.R](./stm.R)

### Python Files
TODO (more details if necessary)

For more information about [area_functions.py](./area_functions.py), [neighborhood_functions.py](./neighborhood_functions.py), and [secondary_processing.py](./secondary_processing.py), please read their docstrings and comments.

***NOTE: some of these files rely on the use of geopandas. As such, a conda env is required. See [Getting Started](#getting-started) for details.***

### R Files
TODO (for stm.R)