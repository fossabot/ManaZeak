import json
import math

import os

from django.http.response import JsonResponse
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

from app.models import Track, Artist, Album
from app.utils import badFormatError


def scanLibrary(library, playlist, convert):
    failedItems = []
    for root, dirs, files in os.walk(library.path):
        for file in files:
            if file.lower().endswith('.mp3'):
                addTrackMP3(root, file, playlist, convert)

            elif file.lower().endswith('.ogg'):
                # TODO: implement
                pass

            elif file.lower().endswith('.flac'):
                # TODO: implement
                pass

            elif file.lower().endswith('.wav'):
                # TODO: implement
                pass

            else:
                failedItems.append(file)

    library.playlist = playlist
    library.save()
    data = {
        'DONE': 'OK',
        'ID': playlist.id,
        'FAILS': failedItems,
    }
    return data


def addTrackMP3(root, file, playlist, convert):
    track = Track()

    # --- FILE INFORMATION ---
    audioFile = MP3(root + "/" + file)
    track.location = root + "/" + file
    track.size = os.path.getsize(root + "/" + file)
    track.bitRate = audioFile.info.bitrate
    track.duration = audioFile.info.length
    track.sampleRate = audioFile.info.sample_rate
    track.bitRateMode = audioFile.info.bitrate_mode

    # --- FILE TAG ---
    audioTag = ID3(root + "/" + file)
    if convert:
        audioTag.update_to_v24()
        audioTag.save()
    audioTag = ID3(root + "/" + file)

    if 'TIT2' in audioTag:
        if not audioTag['TIT2'].text[0] == "":
            track.title = audioTag['TIT2'].text[0]

    if 'TDRC' in audioTag:
        if not audioTag['TDRC'].text[0].get_text() == "":
            track.year = audioTag['TDRC'].text[0].get_text()[:4]  # Date of Recording

    totalTrack = 0
    totalDisc = 1
    if 'TRCK' in audioTag:
        if not audioTag['TRCK'].text[0] == "":
            if "/" in audioTag['TRCK'].text[0]:  # Contains info about the album number of track
                tags = audioTag['TRCK'].text[0].split('/')
                track.number = tags[0]
                totalTrack = tags[1]
            else:
                track.number = audioTag['TRCK'].text[0]

    if 'TCOM' in audioTag:
        if not audioTag['TCOM'].text[0] == "":
            track.composer = audioTag['TCOM'].text[0]

    if 'TOPE' in audioTag:
        if not audioTag['TOPE'].text[0] == "":
            track.performer = audioTag['TOPE'].text[0]

    if 'TBPM' in audioTag:
        if not audioTag['TBPM'].text[0] == "":
            track.bpm = math.floor(float(audioTag['TBPM'].text[0]))

    if 'COMM' in audioTag:
        if not audioTag['COMM'].text[0] == "":
            track.comment = audioTag['COMM'].text[0]

    if 'USLT' in audioTag:
        if not audioTag['USLT'].text[0] == "":
            track.lyrics = audioTag['USLT'].text[0]

    if len(audioTag.getall('TXXX')) != 0:
        for txxx in audioTag.getall('TXXX'):
            if txxx.desc == 'TOTALDISCS':
                totalDisc = txxx.text[0]

    # --- Save data for many-to-many relationship registering ---
    track.save()

    # --- Adding artist to DB ---
    if 'TPE1' in audioTag:  # Check if artist exists
        artists = audioTag['TPE1'].text[0].split(",")
        for artistName in artists:
            artistName = artistName.lstrip()  # Remove useless spaces at the beginning
            num_results = Artist.objects.filter(name=artistName).count()
            if num_results == 0:  # The artist doesn't exist
                artist = Artist()
                artist.name = artistName
                artist.save()
            artist = Artist.objects.get(name=artistName)
            track.artist.add(artist)
    else:
        # TODO default value of artist (see if it's possible)
        pass

    # --- Adding album to DB ---
    if 'TALB' in audioTag:
        albumTitle = audioTag['TALB'].text[0]
        if Album.objects.filter(title=albumTitle).count() == 0:  # If the album doesn't exist
            album = Album()
            album.title = albumTitle
            album.numberTotalTrack = totalTrack
            album.numberOfDisc = totalDisc
            album.save()
            for trackArtist in track.artist.all():
                album.artist.add(trackArtist)
        album = Album.objects.get(title=albumTitle)
        # Check for each artist if he exists in the album
        for trackArtist in track.artist.all():
            if album.artist.filter(name=trackArtist.name).count() == 0:  # The Artist wasn't added
                album.artist.add(trackArtist)
                album.save()
        track.album = album
        track.save()
    else:
        # TODO default value of artist (see if it's possible)
        pass

    # --- Adding track to playlist --- #
    playlist.track.add(track)


# TODO: TEST this with front
# Change the permission of the song for the web server
def changePermission(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        try:  # Current song if protected next song is exposed.
            if 'CURR_ID' in response:
                trackId = response['CURR_ID']
                track = Track.objects.get(id=trackId)
                os.chmod(track.location, 0o600)
            else:
                badFormatError()
            if 'NEXTID' in response:
                trackId = response['URL']
                track = Track.objects.get(id=trackId)
                os.chmod(track.location, 0o666)
            else:
                badFormatError()
            data = {
                'RESULT': 'DONE',
            }
            return JsonResponse(data)
        except AttributeError:
            badFormatError()
