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

try:
  #we try to access django settings for the web interface to access
  #the samed databas (via django settings file)
  
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webserver.settings")
  from futaba_archive import models as bdmodels                  
except ImportError:
  print 'Could not specify DJANGO_SETTINGS_MODULE via django settings module. Failing'
  sys.exit(-1)

#TODO: Store boards to archive in db
urls = [ 
  'http://dat.2chan.net/img2/futaba.htm', #nijigen gazou keijiban ('2D' Image Board)
  'http://dec.2chan.net/b/futaba.htm', #nijigen ura '/b/' board ('Alt 2D')
  ]

def update_archive(url):
  print '----{url}----'.format(url=url)
  threads = get_threads(url)
  for thread in threads:
    print unicode(thread)
  print '----{url}----'.format(url=url)

def main():
  parser = argparse.ArgumentParser(description='Crawl futaba board, updating archive from boards every X minutes')
  #parser.add_argument('-u', '--url',  help='url to fetch for scraping.', type=str, default='http://dat.2chan.net/img2/futaba.htm')
  args = parser.parse_args()

  #starting scheduler in standalone mode. All jobs run in this thread.
  #Allows us to sequentially check N boards in sequence.
  scheduler = Scheduler(standalone=True)

  for url in urls:
    scheduler.add_interval_job(update_archive, minutes=3, kwargs={'url': url})

  scheduler.start()


if __name__ == "__main__":
  main()
