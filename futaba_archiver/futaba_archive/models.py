# vim: set ts=2 expandtab:
from django.db import models

class Post(models.Model):
  title = models.CharField(max_length=128)
  poster = models.CharField(max_length=128)
  date = models.DateTimeField('date published')
  number = models.IntegerField()
  image = models.CharField(max_length=256)
  thumbnail = models.CharField(max_length=256)
  text = models.CharField(max_length=1024)
  parent = models.ForeignKey('self', null=True, blank=True, related_name='response', related_query_name='response')
