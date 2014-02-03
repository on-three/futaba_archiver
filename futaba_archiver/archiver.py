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
except ImportError:
  print 'Could not specify DJANGO_SETTINGS_MODULE via django settings module. Failing'
  sys.exit(-1)

#TODO: Store boards to archive in db
urls = { 
  '2d_images' :  'http://dat.2chan.net/img2/futaba.htm', #nijigen gazou keijiban ('2D' Image Board)
  'b' : 'http://dec.2chan.net/b/futaba.htm', #nijigen ura '/b/' board ('Alt 2D')
  }
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
    print 'path ' + path
    if not os.path.exists(path):
      print 'Gonna create dir ' + path
      os.makedirs(path, mode=0775)
      uid = pwd.getpwnam(username).pw_uid
      gid = grp.getgrnam(groupname).gr_gid
      os.chown(path, uid, gid)
  except OSError as error:
    print(error)
    print(error.args)
    print(error.filename)
    

def update_archive_db(board, thread, write=False):
  '''
  Update django database with info on a single thread,
  including its posts, images and responses etc.
  arg: thread: futaba_scrape.Post object with thread info
  '''
  #print unicode(thread)
  #make sure a destination directory for images and thumbnails exist
  #permissions to create directories must be managed elsewhere
  IMAGE_DEST_DIR = STATIC_FILE_PATH + '/'+ board + '/' + IMAGE_DIR
  THUMBNAIL_DEST_DIR = STATIC_FILE_PATH + '/' + board + '/' + THUMBNAIL_DIR
  print 'images ' + IMAGE_DEST_DIR
  print 'thumbs ' + THUMBNAIL_DEST_DIR
  requires_directory(IMAGE_DEST_DIR, 'www-data', 'www-data')
  requires_directory(THUMBNAIL_DEST_DIR, 'www-data', 'www-data')

  d = datetime.fromtimestamp(mktime(thread.time))
  dbp = DBPost(title=thread.title, poster=thread.name, date=d, number=thread.number, image=thread.image, thumbnail=thread.thumbnail, text=thread.text)
  if write:
    dbp.save()
  for post_number, response in thread.responses.iteritems():
    d2 = datetime.fromtimestamp(mktime(response.time))
    r = DBPost(title=response.title, poster=response.name, date=d2, number=response.number, image=response.image, thumbnail=response.thumbnail, text=response.text, parent=dbp)
    if write:
      r.save()


def update_archive(board, url, write_to_db=False):
  print '++++{board}:{url}++++'.format(board=board, url=url)
  threads = get_threads(url)
  print 'number of threads ' + url +' ' + str(len(threads))
  for thread in threads:
    #print unicode(thread)
    update_archive_db(board, thread, write_to_db)
  print '----{board}:{url}----'.format(board=board, url=url)

def main():
  parser = argparse.ArgumentParser(description='Crawl futaba board, updating archive from boards every X minutes')
  parser.add_argument('-i', '--image_path',  help='system path where to store images', type=str, default='/var/www/futaba_archive/')
  parser.add_argument('-d', '--write_to_database', help='Turn on storing of data in django db.', action='store_true')
  parser.add_argument('-t', '--time_between_updates', help='Number of minutes between scrapes of boards.', type=int, default=3)
  args = parser.parse_args()

  #appscheduler is too difficult to control (multiple jobs run simultaneously, not good for http requests to same site)
  #so i'm just hacking it here.
  while True:
    for board, url in urls.iteritems():
      update_archive(board, url, args.write_to_database)
    sleep(args.time_between_updates*SECONDS_TO_MINUTES)
      
  

if __name__ == "__main__":
  main()
