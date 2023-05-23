import sys
sys.path.append("/projects/p31502/projects/craigslist/")

from secondary_processing import html_to_csv_dump, process_csvs
from filter_html import filter_html,reverse_filter

import argparse
import time

def parse_commandline():
    """Parse the arguments given on the command-line.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metro_area",
                       help="Name of metro_area",
                       default=None)


    args = parser.parse_args()

    return args.metro_area

if __name__ == '__main__':
    args = parse_commandline()
    if args:
      html_to_csv_dump(args)
      process_csvs(args)
      filter_html(args)
    else:
      html_to_csv_dump()
      process_csvs()
      filter_html()
    #reverse_filter(args)
