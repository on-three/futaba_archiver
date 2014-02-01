#!/usr/bin/python
# vim: set ts=2 expandtab:
"""

Module: archiver.py
Desc: Crawl some boards on futaba archiving posts
Author: on_three
Email: on.three.email@gmail.com
DATE: Friday, February 1st 2014
  
""" 

import os
import os.path
from os.path import expanduser
import re
import uuid
import sys
from time import strftime
import argparse
import string
from apscheduler.scheduler import Scheduler

#from futaba_scrape import scrape_futaba
from futaba_scrape import get_threads
from futaba_scrape import Post

#TODO: Store boards to archive in db
boards = [ 
  'http://dat.2chan.net/img2/futaba.htm', #nijigen gazou keijiban ('2D' Image Board)
  ]

def update_archive():
  print '------------------------------------------------'
  threads = get_threads(boards[0])
  for thread in threads:
    print unicode(thread)

def main():
  parser = argparse.ArgumentParser(description='Crawl futaba board, updating archive from boards every X minutes')
  #parser.add_argument('-u', '--url',  help='url to fetch for scraping.', type=str, default='http://dat.2chan.net/img2/futaba.htm')
  args = parser.parse_args()

  scheduler = Scheduler()

  scheduler.start()

  scheduler.add_interval_job(update_archive, minutes=3)

  while True:
    pass

if __name__ == "__main__":
  main()
