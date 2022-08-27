import sys
sys.path.append("/projects/p31502/projects/craigslist/")

from secondary_processing import html_to_csv_dump, process_csvs

html_to_csv_dump()
process_csvs()
