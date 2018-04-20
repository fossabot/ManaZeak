
# Create an entry in base for a track suggested by a user
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.html import strip_tags
from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.id3._frames import TIT2, TDRC, TPE1, TOPE, TCOM, TRCK, TBPM, USLT, TCON, TALB, TXXX, COMM, TPOS, APIC

from app.models import TrackSuggestion, Artist, Genre
from app.utils import checkPermission, errorCheckMessage


# Create a track suggestion in base or update it from a user tage edition
from app.wallet import rewardTrackSuggestion


# All the information about a track
class Information:
    trackTitle = None
    trackArtist = None
    trackPerformer = None
    trackComposer = None
    trackYear = None
    trackNumber = None
    trackBPM = None
    trackGenre = None
    albumTitle = None
    albumArtist = None
    albumTotalDisc = None
    albumDiscNumber = None
    albumTotalTrack = None
    comment = None
    lyrics = None
    cover = None


# Update the file information locally
def updateFileMetadata(track, tags):
    if track.location.endswith(".mp3"):
        # Check if the file has a tag header
        audioTag = ID3()
        if tags.trackTitle is not None:
            audioTag.add(TIT2(text=tags.trackTitle))
        if tags.trackYear is not None:
            audioTag.add(TDRC(text=str(tags.trackYear)))
        if tags.trackArtist is not None:
            audioTag.add(TPE1(text=tags.trackArtist))
        if tags.trackPerformer is not None:
            audioTag.add(TOPE(text=tags.trackPerformer))
        if tags.trackComposer is not None:
            audioTag.add(TCOM(text=tags.trackComposer))
        if tags.trackNumber is not None:
            if tags.albumTotalTrack is not None:
                audioTag.add(TRCK(text=str(tags.trackNumber) + "/" + str(tags.albumTotalTrack)))
            else:
                audioTag.add(TRCK(text=str(tags.trackNumber)))
        if tags.trackBPM is not None:
            audioTag.add(TBPM(text=str(tags.trackBPM)))
        if tags.lyrics is not None:
            audioTag.add(USLT(text=tags.lyrics))
        if tags.trackGenre is not None:
            audioTag.add(TCON(text=tags.trackGenre))
        if tags.albumTitle is not None:
            audioTag.add(TALB(text=tags.albumTitle))
        if tags.albumArtist is not None:
            audioTag.add(TPE1(text=tags.albumArtist))
        if tags.albumTotalDisc is not None:
            audioTag.add(TXXX(desc="TOTALDISCS", text=[tags.albumTotalDisc]))
        if tags.comment is not None:
            audioTag.add(COMM(text=tags.comment))
        if tags.albumDiscNumber is not None:
            audioTag.add(TPOS(text=str(tags.albumDiscNumber)))
        if tags.cover is not None:
            audioTag.add(APIC(data=tags.cover, type=3))
        audioTag.save(track.location)
        data = errorCheckMessage(True, None)
    elif track.location.endswith(".flac"):
        audioTag = FLAC(track.location)
        if tags.trackTitle is not None:
            audioTag["TITLE"] = tags.trackTitle
        if tags.trackYear is not None:
            audioTag['DATE'] = str(tags.trackYear)
        if tags.trackArtist is not None:
            audioTag['ARTIST'] = tags.trackArtist
        if tags.trackPerformer is not None:
            audioTag['PERFORMER'] = tags.trackPerformer
        if tags.trackComposer is not None:
            audioTag['COMPOSER'] = tags.trackComposer
        if tags.trackNumber is not None:
            audioTag['TRACKNUMBER'] = str(tags.trackNumber)
        if tags.albumTotalTrack is not None:
            audioTag['TOTALTRACK'] = str(tags.albumTotalTrack)
        if tags.trackBPM is not None:
            audioTag['BPM'] = tags.trackBPM
        if tags.lyrics is not None:
            audioTag['LYRICS'] = tags.lyrics
        if tags.trackGenre is not None:
            audioTag['GENRE'] = tags.trackGenre
        if tags.albumTitle is not None:
            audioTag['ALBUM'] = tags.albumTitle
        if tags.albumArtist is not None:
            audioTag['ARTIST'] = tags.albumArtist
        if tags.albumTotalDisc is not None:
            audioTag['TOTALDISC'] = str(tags.albumTotalDisc)
        if tags.albumDiscNumber is not None:
            audioTag['DISCNUMBER'] = str(tags.albumDiscNumber)
        if tags.comment is not None:
            audioTag['COMMENT'] = str(tags.comment)
        if tags.cover is not None:
            picture = audioTag.pictures
            picture[0].data = tags.cover
        audioTag.save(track.location)
        data = errorCheckMessage(True, None)
    else:
        data = errorCheckMessage(False, "formatError")
    return data


def createTrackSuggestion(trackInformation, track, user):
    if checkPermission(["TAGS"], user):
        # Checking if the user already made a suggestion on the track
        if TrackSuggestion.objects.find(user=user, track=track).count() == 1:
            trackSuggestion = TrackSuggestion.objects.get(user=user, track=track)
        else:
            trackSuggestion = TrackSuggestion()
            trackSuggestion.user = user
            trackSuggestion.trackReference = track

        # Filling the information about the track
        if trackInformation.trackPerformer is not None:
            trackSuggestion.performer = trackInformation.trackPerformer

        if trackInformation.trackComposer is not None:
            trackSuggestion.composer = trackInformation.trackComposer

        if trackInformation.trackNumber is not None:
            trackSuggestion.number = trackInformation.trackNumber

        if trackInformation.trackYear is not None:
            trackSuggestion.year = trackInformation.trackYear

        if trackInformation.trackTitle is not None:
            trackSuggestion.title = trackInformation.trackTitle

        if trackInformation.trackBPM is not None:
            trackSuggestion.bpm = trackInformation.trackBPM

        if trackInformation.trackArtist is not None:
            trackSuggestion.artist = trackInformation.trackArtist

        if trackInformation.comment is not None:
            trackSuggestion.comment = trackInformation.comment

        if trackInformation.lyrics is not None:
            trackSuggestion.lyrics = trackInformation.lyrics

        if trackInformation.cover is not None:
            trackSuggestion.coverLocation = trackInformation.cover

        if trackInformation.trackGenre is not None:
            trackSuggestion.genre = trackInformation.trackGenre

        if trackInformation.albumDiscNumber is not None:
            trackSuggestion.discNumber = trackInformation.albumDiscNumber

        if trackInformation.albumTitle is not None:
            trackSuggestion.album = trackInformation.albumTitle

        # Saving the track to database
        trackSuggestion.save()
        data = errorCheckMessage(True, None)
    else:
        data = errorCheckMessage(False, "permissionError")
    # Checking if the user can create a suggestion
    return data


# Find a track suggestion id given in database and update the track in the
#  database linked to the suggestion
@login_required(redirect_field_name='login.html', login_url='app:login')
def applySuggestion(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        user = request.user
        if checkPermission(['TAGE'], user):
            if 'SUGGESTION_ID' in response:
                suggestionId = strip_tags(response['SUGGESTION_ID'])
                if TrackSuggestion.objects.find(id=suggestionId, user=user).count() == 1:
                    trackSuggestion = TrackSuggestion.objects.get(id=suggestionId)
                    data = updateTrackFromSuggestion(trackSuggestion, user)
                else:
                    data = errorCheckMessage(False, "dbError")
            else:
                data = errorCheckMessage(False, "badFormat")
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Update the track tags from a track suggestion
def updateTrackFromSuggestion(trackSuggestion, user):
    if trackSuggestion.trackReference is not None:
        # Getting the original track
        track = trackSuggestion.trackReference
        tags = Information()
        tagsAccepted = 0

        # Checking if the tag changed and reward points
        if trackSuggestion.title is not None and track.title != trackSuggestion.title:
            tagsAccepted += 1
            track.title = trackSuggestion.title
            tags.trackTitle = track.title

        if trackSuggestion.bpm is not None and track.bpm != trackSuggestion.bpm:
            tagsAccepted += 1
            track.bpm = trackSuggestion.bpm
            tags.trackBPM = track.bpm

        if trackSuggestion.year is not None and track.year != trackSuggestion.year:
            tagsAccepted += 1
            track.year = trackSuggestion.year
            tags.trackYear = track.year

        if trackSuggestion.number is not None and track.number != trackSuggestion.number:
            tagsAccepted += 1
            track.number = trackSuggestion.number
            tags.trackNumber = track.number

        if trackSuggestion.composer is not None and track.composer != trackSuggestion.composer:
            tagsAccepted += 1
            track.composer = trackSuggestion.composer
            tags.trackComposer = track.composer

        if trackSuggestion.performer is not None and track.performer != trackSuggestion.performer:
            tagsAccepted += 1
            track.performer = trackSuggestion.performer
            tags.trackPerformer = track.performer

        if trackSuggestion.comment is not None and track.comment != trackSuggestion.comment:
            tagsAccepted += 1
            track.comment = trackSuggestion.comment
            tags.comment = track.commment

        if trackSuggestion.coverLocation is not None and track.coverLocation != TrackSuggestion.coverLocation:
            tagsAccepted += 1
            track.coverLocation = trackSuggestion.coverLocation
            tags.cover = track.coverLocation

        if trackSuggestion.lyrics is not None and track.lyrics != trackSuggestion.lyrics:
            tagsAccepted += 1
            track.lyrics = TrackSuggestion.lyrics
            tags.lyrics = track.lyrics

        # Checking if the suggestion contained artists
        if len(trackSuggestion.artist) > 0:
            artists = []
            for artist in trackSuggestion.artist:
                # Create the artist if he doesn't exists
                if Artist.objects.find(name=artist).count() == 0:
                    artist = Artist()
                    artist.name = artist
                    artist.save()
                    artists.append(artist)
                    tags.trackArtist.append()
            track.artist = artists

        if trackSuggestion.genre is not None:
            genreName = trackSuggestion.genre
            if Genre.objects.find(name=genreName).count() == 0:
                genre = Genre()
                genre.name = genreName
                genre.save()
                tags.trackGenre = genreName
            genre = Genre.objects.get(name=genreName)
            track.genre = genre

        track.save()

        # Saving track information into the audio file
        updateFileMetadata(track, tags)

        # Reward the user with the correct tag
        rewardTrackSuggestion(tagsAccepted, user, True)
        data = errorCheckMessage(True, None)
    else:
        data = errorCheckMessage(False, "dbError")
    return data
