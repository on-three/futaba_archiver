# vim: set ts=2 expandtab:
from django.contrib import admin
from futaba_archive.models import Post

class PostAdmin(admin.ModelAdmin):
  list_display = ('number', 'date', 'is_thread')

admin.site.register(Post, PostAdmin)
