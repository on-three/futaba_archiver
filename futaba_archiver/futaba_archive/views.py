# vim: set ts=2 expandtab:
from django.shortcuts import render
from django.template import Context, loader
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from futaba_archive.models import Board

def index(request):
  boards = Board.objects.all()
  t = loader.get_template('futaba_archive/index.html')
  c = Context({
    'boards': boards,
    })
  return HttpResponse(t.render(c))

def board(request, board_name):
  '''
  Display a certain number of threads on a given board
  '''
  board = Board.objects.get(name=board_name)
  if not board:
    return HttpResponseNotFound('<h1>Board not found</h1>')
  
  threads = board.post_set.filter(parent=None)
  t = loader.get_template('futaba_archive/board.html')
  c = Context({
    'board': board,
    'threads' : threads,
    })
  return HttpResponse(t.render(c))

def thread(request, board_name, post_number):
  '''
  Display thread and all responses
  '''
  board = Board.objects.get(name=board_name)
  if not board:
    return HttpResponseNotFound('<h1>Board not found</h1>')

  thread = board.post_set.get(number=post_number)
  if not thread:
    return HttpResponseNotFound('<h1>Thread not found</h1>')
  
  posts = thread.post_set.all()
  t = loader.get_template('futaba_archive/thread.html')
  c = Context({
    'thread':thread,
    'board':board,
    'posts':posts,
    })
  return HttpResponse(t.render(c))
