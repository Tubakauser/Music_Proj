from django.contrib import admin
from . models import Song,Playlist,Favourite,Recent

admin.site.register(Song)
admin.site.register(Playlist)
admin.site.register(Favourite)
admin.site.register(Recent)


