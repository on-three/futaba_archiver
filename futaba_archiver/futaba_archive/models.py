# vim: set ts=2 expandtab:
from django.db import models

class Board(models.Model):
  '''
  Encapsulate data describing a yotsuba board
  '''
  name = models.CharField(max_length=128)
  url = models.CharField(max_length=512)

class Post(models.Model):
  '''
  Encapsulates data from a single futaba image board post.
  The data can represent a thread or responses.
  '''
  board = models.ForeignKey('Board')
  title = models.CharField(max_length=128)
  poster = models.CharField(max_length=128)
  date = models.DateTimeField('date published')
  number = models.IntegerField()
  image = models.CharField(max_length=256)
  thumbnail = models.CharField(max_length=256)
  text = models.CharField(max_length=1024)
  parent = models.ForeignKey('self', null=True, blank=True, related_name='response', related_query_name='response')

  def board_name(self):
    '''
    Access foreign key board name for list views
    '''
    return self.board.name

  def is_thread(self):
    return self.parent is None
