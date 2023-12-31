from django.shortcuts import render,redirect
from project_app.models import Song,Recent,Favourite,Playlist
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index(request):

    #Display recent songs
    if not request.user.is_anonymous :
        recent = list(Recent.objects.filter(user=request.user).values('song_id').order_by('-id'))
        recent_id = [each['song_id'] for each in recent][:5]
        recent_songs_unsorted = Song.objects.filter(song_id__in=recent_id,recent__user=request.user)
        recent_songs = list()
        for id in recent_id:
            recent_songs.append(recent_songs_unsorted.get(song_id=id))
    else:
        recent = None
        recent_songs = None

    first_time = False
    #Last played song
    if not request.user.is_anonymous:
        last_played_list = list(Recent.objects.filter(user=request.user).values('song_id').order_by('-id'))
        if last_played_list:
            last_played_id = last_played_list[0]['song_id']
            last_played_song = Song.objects.get(song_id=last_played_id)
        else:
            first_time = True
            last_played_song = Song.objects.get(song_id=7)

    else:
        first_time = True
        last_played_song = Song.objects.get(song_id=7)

    #Display all songs
    songs = Song.objects.all()

    #Display few songs on home page
    songs_all = list(Song.objects.all().values('song_id').order_by('?'))
    sliced_ids = [each['song_id'] for each in songs_all][:5]
    indexpage_songs = Song.objects.filter(song_id__in=sliced_ids)



    if len(request.GET) > 0:
        search_query = request.GET.get('q')
        filtered_songs = songs.filter(Q(name__icontains=search_query)).distinct()
        context = {'all_songs': filtered_songs,'last_played':last_played_song,'query_search':True}
        return render(request, 'pro_app/index.html', context)

    context = {
        'all_songs':indexpage_songs,
        'recent_songs': recent_songs,
        'last_played':last_played_song,
        'first_time': first_time,
        'query_search':False,
    }
    return render(request, 'pro_app/index.html', context=context)

def songpost(request, id):
    song = Song.objects.filter(song_id = id).first()
    return render(request, 'pro_app/songpost.html', {'song': song})


@login_required(login_url='login')
def play_song(request, song_id):
    songs = Song.objects.filter(song_id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs,user=request.user).values()):
        data = Recent.objects.filter(song=songs,user=request.user)
        data.delete()
    data = Recent(song=songs,user=request.user)
    data.save()
    return redirect('all_songs')


def all_songs(request):
    songs = Song.objects.all()

    first_time = False
    last_played_song = None  # Set a default value for last_played_song


    #Last played song
    if not request.user.is_anonymous:
        last_played_list = list(Recent.objects.filter(user=request.user).values('song_id').order_by('-id'))
        if last_played_list:
            last_played_id = last_played_list[0]['song_id']
            last_played_song = Song.objects.get(song_id=last_played_id)
    else:
        first_time = True
        last_played_song = Song.objects.get(song_id=7)

    
    
    
    context = {
        'songs': songs,
        'last_played':last_played_song,
        'first_time':first_time,
        'query_search' : False,
        }
    return render(request, 'pro_app/all_songs.html', context=context)


@login_required(login_url='login')
def detail(request, song_id):
    songs = Song.objects.filter(song_id=song_id).first()

    # Add data to recent database
    if list(Recent.objects.filter(song=songs,user=request.user).values()):
        data = Recent.objects.filter(song=songs,user=request.user)
        data.delete()
    data = Recent(song=songs,user=request.user)
    data.save()

    #Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(song_id=last_played_id)
    else:
        last_played_song = Song.objects.get(id=7)


    playlists = Playlist.objects.filter(user=request.user).values('playlist_name').distinct
    is_favourite = Favourite.objects.filter(user=request.user).filter(song=song_id).values('is_fav')

    if request.method == "POST":
        if 'playlist' in request.POST:
            playlist_name = request.POST["playlist"]
            q = Playlist(user=request.user, song=songs, playlist_name=playlist_name)
            q.save()
            messages.success(request, "Song added to playlist!")
        elif 'add-fav' in request.POST:
            is_fav = True
            query = Favourite(user=request.user, song=songs, is_fav=is_fav)
            print(f'query: {query}')
            query.save()
            messages.success(request, "Added to favorite!")
            return redirect('detail', song_id=song_id)
        elif 'rm-fav' in request.POST:
            is_fav = True
            query = Favourite.objects.filter(user=request.user, song=songs, is_fav=is_fav)
            print(f'user: {request.user}')
            print(f'song: {songs.id} - {songs}')
            print(f'query: {query}')
            query.delete()
            messages.success(request, "Removed from favorite!")
            return redirect('detail', song_id=song_id)

    context = {'songs': songs, 'playlists': playlists, 'is_favourite': is_favourite,'last_played':last_played_song}
    return render(request, 'pro_app/detail.html', context=context)



@login_required(login_url='login')
def play_song_index(request, song_id):
    songs = Song.objects.filter(song_id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs,user=request.user).values()):
        data = Recent.objects.filter(song=songs,user=request.user)
        data.delete()
    data = Recent(song=songs,user=request.user)
    data.save()
    return redirect('index')
def playlist(request):
    playlists = Playlist.objects.filter(user=request.user).values('playlist_name').distinct
    context = {'playlists': playlists}
    return render(request, 'pro_app/playlist.html', context=context)


@login_required(login_url='login')
def playlist_songs(request, playlist_name):
    songs = Song.objects.filter(playlist__playlist_name=playlist_name, playlist__user=request.user).distinct()

    if request.method == "POST":
        song_id = list(request.POST.keys())[1]
        playlist_song = Playlist.objects.filter(playlist_name=playlist_name, song__id=song_id, user=request.user)
        playlist_song.delete()
        messages.success(request, "Song removed from playlist!")

    context = {'playlist_name': playlist_name, 'songs': songs}

    return render(request, 'pro_app/playlist_songs.html', context=context)

def favourite(request):
    songs = Song.objects.filter(favourite__user=request.user, favourite__is_fav=True).distinct()
    print(f'songs: {songs}')
    
    if request.method == "POST":
        song_id = list(request.POST.keys())[1]
        favourite_song = Favourite.objects.filter(user=request.user, song_id=song_id, is_fav=True)
        favourite_song.delete()
        messages.success(request, "Removed from favourite!")
    context = {'songs': songs}
    return render(request, 'pro_app/favourite.html', context=context)


def playlist_songs(request, playlist_name):
     songs = Song.objects.filter(playlist__playlist_name=playlist_name, playlist__user=request.user).distinct()
 
     if request.method == "POST":
         song_id = list(request.POST.keys())[1]
         playlist_song = Playlist.objects.filter(playlist_name=playlist_name, song_id=song_id, user=request.user)
         playlist_song.delete()
         messages.success(request, "Song removed from playlist!")
 
     context = {'playlist_name': playlist_name, 'songs': songs}
 
     return render(request, 'pro_app/playlist_songs.html', context=context)


def mymusic(request):
    return render(request, 'pro_app/mymusic.html')


def recent(request):
    
    #Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(song_id=last_played_id)
    else:
        last_played_song = Song.objects.get(song_id=7)

    #Display recent songs
    recent = list(Recent.objects.filter(user=request.user).values('song_id').order_by('-id'))
    if recent and not request.user.is_anonymous :
        recent_id = [each['song_id'] for each in recent]
        recent_songs_unsorted = Song.objects.filter(song_id__in=recent_id,recent__user=request.user)
        recent_songs = list()
        for id in recent_id:
            recent_songs.append(recent_songs_unsorted.get(song_id=id))
    else:
        recent_songs = None

    if len(request.GET) > 0:
        search_query = request.GET.get('q')
        filtered_songs = recent_songs_unsorted.filter(Q(name__icontains=search_query)).distinct()
        context = {'recent_songs': filtered_songs,'last_played':last_played_song,'query_search':True}
        return render(request, 'pro_app/recent.html', context)

    context = {'recent_songs':recent_songs,'last_played':last_played_song,'query_search':False}
    return render(request, 'pro_app/recent.html', context=context)


@login_required(login_url='login')
def play_recent_song(request, song_id):
    songs = Song.objects.filter(song_id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs,user=request.user).values()):
        data = Recent.objects.filter(song=songs,user=request.user)
        data.delete()
    data = Recent(song=songs,user=request.user)
    data.save()
    return redirect('recent')
