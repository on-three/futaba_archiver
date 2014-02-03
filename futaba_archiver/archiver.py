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
from time import mktime
from time import sleep
from datetime import datetime
import argparse
import string
import pwd
import grp
import logging
logging.basicConfig()

SECONDS_TO_MINUTES = 60

#from futaba_scrape import scrape_futaba
from futaba_scrape import get_threads
from futaba_scrape import Post

try:
  #we try to access django settings for the web interface to access
  #the samed databas (via django settings file)
  
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webserver.settings")
  from futaba_archive.models import Post as DBPost
  from futaba_archive.models import Board as DBBoard                  
except ImportError:
  print 'Could not specify DJANGO_SETTINGS_MODULE via django settings module. Failing'
  sys.exit(-1)

#TODO: Store image static destination path in db or in django settings?
#NOTE: management of permissions to create/edit in this path is done here
#you'll have to run this from a user in a group that has permissions
STATIC_FILE_PATH = os.path.dirname(__file__)
IMAGE_DIR='images/'
THUMBNAIL_DIR='thumbnails/'

def requires_directory(path, username, groupname):
  '''
  Create a directory recursively if it doesn't exist.
  Can create with specific user and groupname.
  Permissions to create directory are outside scope of this function.
  '''
  try:
    if not os.path.exists(path):
      os.makedirs(path, mode=0775)
      uid = pwd.getpwnam(username).pw_uid
      gid = grp.getgrnam(groupname).gr_gid
      os.chown(path, uid, gid)
  except OSError as error:
    print(error)
    print(error.args)
    print(error.filename)
    

def update_archive_db(board, thread):
  '''
  Update django database with info on a single thread,
  including its posts, images and responses etc.
  arg: thread: futaba_scrape.Post object with thread info
  '''
  #make sure a destination directory for images and thumbnails exist
  #permissions to create directories must be managed elsewhere
  #TODO: Need to make sure board names are without spaces or odd characters
  IMAGE_DEST_DIR = STATIC_FILE_PATH + '/'+ board.name + '/' + IMAGE_DIR
  THUMBNAIL_DEST_DIR = STATIC_FILE_PATH + '/' + board.name + '/' + THUMBNAIL_DIR
  requires_directory(IMAGE_DEST_DIR, 'www-data', 'www-data')
  requires_directory(THUMBNAIL_DEST_DIR, 'www-data', 'www-data')

  db_time = datetime.fromtimestamp(mktime(thread.time))
  dbp = DBPost(board=board, \
    title=thread.title, \
    poster=thread.name, \
    date=db_time, \
    number=thread.number, \
    image=thread.image, \
    thumbnail=thread.thumbnail, \
    text=thread.text)
  dbp.save()
  for post_number, response in thread.responses.iteritems():
    db_time = datetime.fromtimestamp(mktime(response.time))
    r = DBPost(board=board, \
      title=response.title, \
      poster=response.name, \
      date=db_time, \
      number=response.number, \
      image=response.image, \
      thumbnail=response.thumbnail, \
      text=response.text, \
      parent=dbp)
    r.save()


def update_archive(board):
  print '++++{board}:{url}++++'.format(board=board.name, url=board.url)
  threads = get_threads(board.url)
  print 'number of threads ' + board.url +' ' + str(len(threads))
  for thread in threads:
    #print unicode(thread)
    update_archive_db(board, thread)
  print '----{board}:{url}----'.format(board=board.name, url=board.url)

def main():
  parser = argparse.ArgumentParser(description='Crawl futaba board, updating archive from boards every X minutes')
  parser.add_argument('-i', '--image_path',  help='system path where to store images', type=str, default='/var/www/futaba_archive/')
  parser.add_argument('-t', '--time_between_updates', help='Number of minutes between scrapes of boards.', type=int, default=3)
  args = parser.parse_args()

  #we only read the urls from the database at startup. Restart required for new/chaned boards
  boards = DBBoard.objects.all()

  #appscheduler is too difficult to control (multiple jobs run simultaneously, not good for http requests to same site)
  #so i'm just hacking it here.
  while True:
    for board in boards:
      update_archive(board)
    sleep(args.time_between_updates*SECONDS_TO_MINUTES)
      
  

if __name__ == "__main__":
  main()
