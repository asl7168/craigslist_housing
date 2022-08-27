#!/bin/bash

backup_name="html-$(date +"%m-%d-%y").tar.gz"
tar -zcvf /projects/b1170/craigslist/"${backup_name}" /projects/p31502/projects/craigslist/html/

