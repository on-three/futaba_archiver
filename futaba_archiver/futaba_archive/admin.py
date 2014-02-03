# vim: set ts=2 expandtab:
from django.contrib import admin
from futaba_archive.models import Post
from futaba_archive.models import Board

class BoardAdmin(admin.ModelAdmin):
  list_display = ('name', 'url')

class PostAdmin(admin.ModelAdmin):
  list_display = ('board_name', 'number', 'date', 'is_thread')

admin.site.register(Board, BoardAdmin)
admin.site.register(Post, PostAdmin)
