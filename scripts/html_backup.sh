#!/bin/bash

backup_name="html-$(date +"%m-%d-%y").tar.gz"
tar -zcvf /projects/b1170/corpora/craigslist/backup/"${backup_name}" /projects/b1170/corpora/craigslist/html/
