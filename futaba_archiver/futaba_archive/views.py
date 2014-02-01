# vim: set ts=2 expandtab:
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
  return HttpResponse("Hello, world. You're at the poll index.")
