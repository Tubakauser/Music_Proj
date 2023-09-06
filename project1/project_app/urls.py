from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name ='index'),
    path('songs/<int:id>', views.songpost, name ='songpost'),
    path('play/<int:song_id>/', views.play_song, name ='play_song'),
    path('<int:song_id>/', views.detail, name ='detail'),
    path('play_song/<int:song_id>/', views.play_song_index, name ='play_song_index'),
    path('all_song/',views.all_songs,name ='all_songs'),
    path('playlist/', views.playlist, name ='playlist'),
    path('favourite/', views.favourite, name='favourite'),
    path('playlist/<str:playlist_name>/', views.playlist_songs, name='playlist_songs'),
    path('mymusic/', views.mymusic, name='mymusic'),
    path('recent/', views.recent, name='recent'),
    path('play_recent_song/<int:song_id>/', views.play_recent_song, name='play_recent_song'),




]

