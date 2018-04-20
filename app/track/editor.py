import base64
import hashlib
import json

import os

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.html import strip_tags

from app.models import Track, Artist, Album, Genre, Playlist
from app.track.suggestion import createTrackSuggestion, Information, updateFileMetadata
from app.track.track import exportTrackInfo
from app.utils import errorCheckMessage, checkPermission

from app.wallet import rewardTrackSuggestion


# Check if the value can be converted to int
def checkIntValueError(string):
    try:
        value = int(strip_tags(string).lstrip().rstrip())
    except ValueError:
        value = None
    return value


# Update the track into the database
def updateDBInfo(response, track, user):
    tags = Information()
    tagsChanged = 0
    # Changing tags in the database
    if 'TITLE' in response and response['TITLE'] != '' and track.title != strip_tags(
            response['TITLE']).lstrip().rstrip():
        tags.trackTitle = strip_tags(response['TITLE']).lstrip().rstrip()
        track.title = tags.trackTitle
        tagsChanged += 1

    if 'ARTISTS' in response and response['ARTISTS'] != '':
        tags.trackArtist = strip_tags(response['ARTISTS']).lstrip().rstrip().split(',')
        artists = []
        trackArtist = []
        changed = False

        for artist in track.artist.all():
            trackArtist.append(artist.name)

        for artist in tags.trackArtist:
            if artist not in trackArtist:
                changed = True
                if Artist.objects.filter(name=artist).count() == 0:
                    newArtist = Artist()
                    newArtist.name = artist
                    newArtist.save()
                artists.append(Artist.objects.get(name=artist))

        track.artist.clear()
        for artist in artists:
            track.artist.add(artist)
        if changed:
            tagsChanged += 1

    if 'PERFORMER' in response and response['PERFORMER'] != '' and track.performer != strip_tags(response['PERFORMER']):
        tags.trackPerformer = strip_tags(response['PERFORMER']).lstrip().rstrip()
        track.performer = tags.trackPerformer
        tagsChanged += 1

    if 'COMPOSER' in response and response['COMPOSER'] != '' and track.composer != strip_tags(response['COMPOSER']):
        tags.trackComposer = strip_tags(response['COMPOSER']).lstrip().rstrip()
        track.composer = tags.trackComposer
        tagsChanged += 1

    if 'YEAR' in response and response['YEAR'] != '' and track.year != checkIntValueError(response['YEAR']):
        tags.trackYear = checkIntValueError(response['YEAR'])
        track.year = tags.trackYear
        tagsChanged += 1

    if 'TRACK_NUMBER' in response and response['TRACK_NUMBER'] != '' and track.number != checkIntValueError(
            response['TRACK_NUMBER']):
        tags.trackNumber = checkIntValueError(response['TRACK_NUMBER'])
        track.number = tags.trackNumber
        tagsChanged += 1

    if 'BPM' in response and response['BPM'] != '' and track.bpm != checkIntValueError(response['BPM']):
        track.bpm = checkIntValueError(response['BPM'])
        tagsChanged += 1

    if 'LYRICS' in response and response['LYRICS'] != '' and track.lyrics != strip_tags(response['LYRICS']):
        tags.lyrics = strip_tags(response['LYRICS']).lstrip().rstrip()
        track.lyrics = tags.lyrics
        tagsChanged += 1

    if 'COMMENT' in response and response['COMMENT'] != '' and track.comment != strip_tags(response['COMMENT']):
        tags.comment = strip_tags(response['COMMENT']).lstrip().rstrip()
        track.comment = tags.comment
        tagsChanged += 1

    if 'GENRE' in response and response['GENRE'] != '':
        tags.trackGenre = strip_tags(response['GENRE']).lstrip().rstrip()
        if Genre.objects.filter(name=tags.trackGenre).count() == 0:
            genre = Genre()
            genre.name = tags.trackGenre
            genre.save()
        genre = Genre.objects.get(name=tags.trackGenre)
        if track.genre.name != tags.trackGenre:
            track.genre = genre
            tagsChanged += 1

    if 'COVER' in response:
        if len(response['COVER'].split(",")) > 1:
            md5Name = hashlib.md5()
            if str(response['COVER'].split(",")[0]) == "image/png":
                extension = "png"
            else:
                extension = ".jpg"
            md5Name.update(base64.b64decode(str(response['COVER'].split(",")[1])))
            filePath = "/ManaZeak/static/img/covers/" + md5Name.hexdigest() + extension
            if filePath != track.coverLocation:
                if not os.path.isfile(filePath):
                    with open(filePath, 'wb+') as destination:
                        # Split the header with MIME type
                        tags.cover = base64.b64decode(str(response['COVER'].split(",")[1]))
                        destination.write(tags.cover)
                        track.coverLocation = md5Name.hexdigest() + extension
                    tagsChanged += 1

    if 'ALBUM_TITLE' in response and 'ALBUM_ARTISTS' in response and response['ALBUM_TITLE'] != '' \
            and response['ALBUM_ARTISTS'] != '':
        tags.albumTitle = strip_tags(response['ALBUM_TITLE']).lstrip().rstrip()
        tags.albumArtist = strip_tags(response['ALBUM_ARTISTS']).lstrip().rstrip().split(',')
        if Album.objects.filter(title=tags.albumTitle).count() == 0:
            album = Album()
            album.title = tags.albumTitle
            album.save()
        album = Album.objects.get(title=tags.albumTitle)
        album.artist.clear()
        for artist in tags.albumArtist:
            if Artist.objects.filter(name=artist).count() == 0:
                newArtist = Artist()
                newArtist.name = artist
                newArtist.save()
            album.artist.add(Artist.objects.get(name=artist))

        if 'ALBUM_TOTAL_DISC' in response and response[
            'ALBUM_TOTAL_DISC'] != '' and album.totalDisc != checkIntValueError(response['ALBUM_TOTAL_DISC']):
            tags.albumTotalDisc = checkIntValueError(response['ALBUM_TOTAL_DISC'])
            album.totalDisc = tags.albumTotalDisc
            tagsChanged += 1

        if 'DISC_NUMBER' in response and response['DISC_NUMBER'] != '' and track.discNumber != checkIntValueError(
                response['DISC_NUMBER']):
            tags.albumDiscNumber = checkIntValueError(response['DISC_NUMBER'])
            track.discNumber = tags.albumDiscNumber
            tagsChanged += 1

        if 'ALBUM_TOTAL_TRACK' in response and response[
            'ALBUM_TOTAL_TRACK'] != '' and album.totalTrack != checkIntValueError(response['ALBUM_TOTAL_TRACK']):
            tags.albumTotalTrack = checkIntValueError(response['ALBUM_TOTAL_TRACK'])
            album.totalTrack = tags.albumTotalTrack
            tagsChanged += 1
        album.save()
        if album.title != tags.albumTitle:
            tagsChanged += 1
        track.album = album
    track.save()
    print(tagsChanged)
    rewardTrackSuggestion(tagsChanged, user, True)
    return tags


# Extract all the information about a track
def createTrackInformation(response):
    tags = Information()
    if 'TITLE' in response and response['TITLE'] != '':
        tags.trackTitle = strip_tags(response['TITLE']).lstrip().rstrip()

    if 'ARTISTS' in response and response['ARTISTS'] != '':
        tags.trackArtist = strip_tags(response['ARTISTS']).lstrip().rstrip()

    if 'PERFORMER' in response and response['PERFORMER'] != '':
        tags.trackPerformer = strip_tags(response['PERFORMER']).lstrip().rstrip()

    if 'COMPOSER' in response and response['COMPOSER'] != '':
        tags.trackComposer = strip_tags(response['COMPOSER']).lstrip().rstrip()

    if 'YEAR' in response and response['YEAR'] != '':
        tags.trackYear = checkIntValueError(response['YEAR'])

    if 'TRACK_NUMBER' in response and response['TRACK_NUMBER'] != '':
        tags.trackNumber = checkIntValueError(response['TRACK_NUMBER'])

    if 'BPM' in response and response['BPM'] != '':
        tags.trackBPM = checkIntValueError(response['BPM'])

    if 'LYRICS' in response and response['LYRICS'] != '':
        tags.lyrics = strip_tags(response['LYRICS']).lstrip().rstrip()

    if 'COMMENT' in response and response['COMMENT'] != '':
        tags.comment = strip_tags(response['COMMENT']).lstrip().rstrip()

    if 'GENRE' in response and response['GENRE'] != '':
        tags.trackGenre = strip_tags(response['GENRE']).lstrip().rstrip()

    if 'COVER' in response:
        md5Name = hashlib.md5()
        if str(response['COVER'].split(",")[0]) == "image/png":
            extension = "png"
        else:
            extension = ".jpg"
        if len(response['COVER'].split(",")) > 1:
            md5Name.update(base64.b64decode(str(response['COVER'].split(",")[1])))
            filePath = "/ManaZeak/static/img/covers/" + md5Name.hexdigest() + extension
            if not os.path.isfile(filePath):
                with open(filePath, 'wb+') as destination:
                    # Split the header with MIME type
                    tags.cover = base64.b64decode(str(response['COVER'].split(",")[1]))
                    destination.write(tags.cover)

    if 'ALBUM_TITLE' in response and 'ALBUM_ARTISTS' in response and response['ALBUM_TITLE'] != '' \
            and response['ALBUM_ARTISTS'] != '':
        tags.albumTitle = strip_tags(response['ALBUM_TITLE']).lstrip().rstrip()
        tags.albumArtist = strip_tags(response['ALBUM_ARTISTS']).lstrip().rstrip().split(',')

        if 'ALBUM_TOTAL_DISC' in response and response['ALBUM_TOTAL_DISC'] != '':
            tags.albumTotalDisc = checkIntValueError(response['ALBUM_TOTAL_DISC'])

        if 'DISC_NUMBER' in response and response['DISC_NUMBER'] != '':
            tags.albumDiscNumber = checkIntValueError(response['DISC_NUMBER'])

        if 'ALBUM_TOTAL_TRACK' in response and response['ALBUM_TOTAL_TRACK'] != '':
            tags.albumTotalTrack = checkIntValueError(response['ALBUM_TOTAL_TRACK'])
    return tags


# Create a tag suggestion or edit tag depending of the user privileges
@login_required(redirect_field_name='login.html', login_url='app:login')
def changeTracksMetadata(request):
    if request.method == 'POST':
        user = request.user
        response = json.loads(request.body)
        if 'TRACKS_ID' in response:
            trackIds = response['TRACKS_ID']
            data = {}
            for trackId in trackIds:
                trackId = checkIntValueError(trackId)
                if trackId is not None:
                    if Track.objects.filter(id=trackId).count() == 1:
                        track = Track.objects.get(id=trackId)

                        # If the user can't edit tag
                        if checkPermission(["TAGE"], user):
                            # Updating database information
                            tags = updateDBInfo(response, track, user)
                            # Changing tags in the file
                            data = updateFileMetadata(track, tags)
                            for playlist in Playlist.objects.filter(track__id=track.id):
                                if not playlist.refreshView:
                                    playlist.refreshView = True
                                    playlist.save()

                        # Check if the user can submit a suggestion
                        elif checkPermission(["TAGS"], user):
                            tags = createTrackInformation(response)
                            createTrackSuggestion(tags, track, user)
                            data = errorCheckMessage(False, "badFormat")
                        else:
                            data = errorCheckMessage(False, "permissionError")
                    else:
                        data = errorCheckMessage(False, "dbError")
                else:
                    data = errorCheckMessage(False, "valueError")
        else:
            data = errorCheckMessage(False, "badFormat")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


@login_required(redirect_field_name='login.html', login_url='app:login')
def getBufferTracks(request):
    if request.method == 'GET':
        user = request.user
        if checkPermission(["UPAP"], user):
            tracks = Track.objects.filter(playlist=None)
            data = []
            for track in tracks:
                data.append(exportTrackInfo(track))
            response = dict({'RESULT': data})
        else:
            response = errorCheckMessage(False, "permissionError")
    else:
        response = errorCheckMessage(False, "badRequest")
    return JsonResponse(response)
