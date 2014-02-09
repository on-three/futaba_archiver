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
import urllib
from urlparse import urlsplit
from os.path import splitext, basename

SECONDS_TO_MINUTES = 60

from futaba_scrape import get_threads
from futaba_scrape import Post

try:
  #we try to access django settings for the web interface to access
  #the same database (via django settings file)
  
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webserver.settings")
  from futaba_archive.models import Post as DBPost
  from futaba_archive.models import Board as DBBoard
  from django.conf import settings               
except ImportError:
  print 'Could not specify DJANGO_SETTINGS_MODULE via django settings module. Failing'
  sys.exit(-1)

#TODO: Store image static destination path in db or in django settings?
#NOTE: management of permissions to create/edit in this path is done here
#you'll have to run this from a user in a group that has permissions
STATIC_FILE_PATH = settings.LOCAL_STATIC_PATH
IMAGE_DIR='/images/'
THUMBNAIL_DIR='/thumbnails/'

def filename_from_url(url):
  '''
  Estimate filename from a file (here image) URL
  '''
  return os.path.basename(urlsplit(url).path)

def get_file(url, destination):
  '''
  Download image file to indicated path
  returns local full path to file
  '''
  if not url:
    return url
  try:
    filename = filename_from_url(url)
    print 'downloading {file} to {dir} from {url}'.format(file=filename, dir=destination, url=url)
    filepath = destination + filename
    #if a local copy of file exists, don't download again
    if os.path.exists(filepath):
      print 'file {filepath} already exists'.format(filepath=filepath)
      return filename
    urllib.urlretrieve(url, destination + filename)
    return filename
  except Exception as e:
    print str(e)
    return ''
  return ''

def requires_directory(path, username, groupname):
  '''
  Create a directory recursively if it doesn't exist.
  Can create with specific user and groupname.
  Permissions to create directory are outside scope of this function.
  '''
  try:
    if not os.path.exists(path):
      print 'Directory {path} does not exist. Creating it.'.format(path=path)
      os.makedirs(path, mode=0775)
      #uid = pwd.getpwnam(username).pw_uid
      #gid = grp.getgrnam(groupname).gr_gid
      #os.chown(path, uid, gid)
  except OSError as error:
    print(error)
    print(error.args)
    print(error.filename)
    

def update_archive_db(board, thread):
  '''
  Update django database with info on a single thread,
  including its posts, images and responses etc.
  arg: thread: futaba_scrape.Post object with thread info.

  Required board.image_destination_dir and
  board.thumbnail_destination_dir to be defined before
  invoking.
  Can't currently carry those in the db. Or can we?
  '''
  db_time = datetime.fromtimestamp(mktime(thread.time))
  dbp, created = DBPost.objects.get_or_create(number=thread.number, board=board, date=db_time)
  dbp.board = board
  #dbp.title = thread.title
  dbp.poster = thread.name
  dbp.date = db_time
  if not dbp.image:
    dbp.image = get_file(thread.image, board.image_destination_dir)
  if not dbp.thumbnail:
    dbp.thumbnail = get_file(thread.thumbnail, board.thumbnail_destination_dir)
  dbp.text = thread.text
  try:#save() call with raise on a duplicate post number save
    dbp.save()
  except Exception as e:
    print unicode(thread)
    print str(e)
    pass
  for post_number, response in thread.responses.iteritems():
    db_time = datetime.fromtimestamp(mktime(response.time))
    r, created = DBPost.objects.get_or_create(number=response.number, board=board, date=db_time)
    #r.board = response.board
    r.title = response.title
    r.poster = response.name
    r.date = db_time
    r.number = response.number
    if not r.image:
      r.image = get_file(response.image, board.image_destination_dir)
    if not r.thumbnail:
      r.thumbnail = get_file(response.thumbnail, board.thumbnail_destination_dir)
    r.text = response.text
    r.parent = dbp
    try:#save() will raise on a duplicate post number save
      r.save()
    except Exception as e:
      print unicode(response)
      print str(e)
      pass

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
  if not boards:
    print 'No boards provided in current database. FAILING'
    sys.exit(-1)

  #ensure we have static file server destination image file directories for all boards
  #TODO: Need to make sure board names are without spaces or odd characters
  for board in boards:
    IMAGE_DEST_DIR = STATIC_FILE_PATH + board.name + IMAGE_DIR
    THUMBNAIL_DEST_DIR = STATIC_FILE_PATH + board.name + THUMBNAIL_DIR
    requires_directory(IMAGE_DEST_DIR, 'www-data', 'www-data')
    board.image_destination_dir = IMAGE_DEST_DIR
    requires_directory(THUMBNAIL_DEST_DIR, 'www-data', 'www-data')
    board.thumbnail_destination_dir = THUMBNAIL_DEST_DIR

  #appscheduler is too difficult to control (multiple jobs run simultaneously, not good for http requests to same site)
  #so i'm just hacking it here.
  while True:
    for board in boards:
      update_archive(board)
    sleep(args.time_between_updates*SECONDS_TO_MINUTES)
      

if __name__ == "__main__":
  main()
