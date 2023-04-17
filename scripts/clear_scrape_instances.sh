#!/bin/bash

for i in `ps -u asl7168 | grep "firefox\|geckodriver\|python" | awk '{print $1}'`;
	do kill $i;
done
