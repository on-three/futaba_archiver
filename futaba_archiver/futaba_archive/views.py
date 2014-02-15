# vim: set ts=2 expandtab:
from django.shortcuts import render
from django.template import Context, loader
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
  
  threads = board.post_set.filter(parent=None).order_by('-date')
  paginator = Paginator(threads, 15) #15 threads per page
  page = request.GET.get('page')
  try:
    threads = paginator.page(page)
  except PageNotAnInteger:
    # If page is not an integer, deliver first page.
    threads = paginator.page(1)
  except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
    threads = paginator.page(paginator.num_pages)

  for thread in threads:
    thread.responses = list(thread.post_set.order_by('number').all())
    if thread.responses:
      def add_response_index(response, index):
        response.response_index = index+1
        return response
      thread.responses = [ add_response_index(x, i) for i, x in enumerate(thread.responses)][-5:]
  prev_pages = [ x for x in range(threads.number-5, threads.number) if x>0]
  next_pages = [ x for x in range(threads.number+1, threads.number+6) if x<= paginator.num_pages ]

  t = loader.get_template('futaba_archive/board.html')
  c = Context({
    'board': board,
    'threads' : threads,
    'prev_pages' : prev_pages,
    'next_pages' : next_pages,
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
