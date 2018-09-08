#!/bin/bash
for i in 2010 2011 2012 2013 2014 2015 2016 2017
do
    python3 get_data.py 2000 $i
    python3 get_data.py 2000 $i --surface
    python3 get_data.py $i $(($i + 1)) --odds
    python3 get_data.py $i $(($i + 1)) --surface --odds
done
