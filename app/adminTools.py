import json
import os

import requests
from django import db
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.html import strip_tags
from multiprocessing import Process

from app.collection.library import deleteLibrary
from app.dao import deleteView
from app.models import Track, Artist, Album, Playlist, Library, Genre, Shuffle, UserHistory, Stats, History, \
    AdminOptions, UserPreferences, InviteCode, Groups, Permissions
from app.collection.playlist import getTotalLength
from app.track.importer import regenerateCover
from app.user import deleteLinkedEntities
from app.utils import errorCheckMessage, timeCodeToString, checkPermission
from app.wallet import calculateCurrentAvailableCash


def getAdminOptions():
    # If a abnormal number of admin options
    if AdminOptions.objects.all().count() > 1:
        AdminOptions.objects.all().delete()

    # If no admin options exists
    if AdminOptions.objects.all().count() == 0:
        adminOptions = AdminOptions()
        adminOptions.save()

    # If a normal number of admin options exists
    else:
        adminOptions = AdminOptions.objects.all().first()
    return adminOptions


# Get all the information needed for the admin view
@login_required(redirect_field_name='login.html', login_url='app:login')
def getAdminView(request):
    if request.method == 'GET':
        user = request.user
        if checkPermission(["ADMV"], user):
            adminOptions = getAdminOptions()
            users = User.objects.all().order_by('date_joined')
            userInfo = []

            # User information
            for user in users:
                dateJoined = timeCodeToString(user.date_joined)
                lastLogin = timeCodeToString(user.last_login)
                userPreferences = UserPreferences.objects.get(user=user)
                inviteCode = InviteCode.objects.get(user=user)
                godfather = {
                    'GODFATHER_NAME': "Jesus",
                    "GODFATHER_CODE": "Christ",
                }
                if userPreferences.inviteCode is not None:
                    godfather = {
                        'GODFATHER_NAME': userPreferences.inviteCode.user.username,
                        'GODFATHER_CODE': userPreferences.inviteCode.code,
                    }
                userInfo.append({**{
                    'NAME': user.username,
                    'IS_ADMIN': user.is_superuser,
                    'JOINED': dateJoined,
                    'LAST_LOGIN': lastLogin,
                    'USER_ID': user.id,
                    'INVITE_CODE': inviteCode.code,
                    'MANACOIN': calculateCurrentAvailableCash(userPreferences.wallet),
                    'GROUP_ID': userPreferences.group.id,
                    'GROUP_NAME': userPreferences.group.name,
                }, **godfather})
            data = dict({'USER': userInfo})

            # Library information
            libraryInfo = []
            for library in Library.objects.all():
                libraryInfo.append({
                    'NAME': library.playlist.name,
                    'PATH': library.path,
                    'NUMBER_TRACK': library.playlist.track.all().count(),
                    'TOTAL_DURATION': getTotalLength(library.playlist),
                    'ID': library.id,
                })
            data = {**data, **dict({'LIBRARIES': libraryInfo})}
            # Global options
            data = {**data, **{
                'SYNC_KEY': adminOptions.syncthingKey,
                'BUFFER_PATH': adminOptions.bufferPath,
                'INVITE_ENABLED': adminOptions.inviteCodeEnabled,
            }}
            groupInfo = []
            for group in Groups.objects.all().order_by("-rank"):
                permissions = []
                for permission in group.permissions.all():
                    permissions.append(permission.code)
                groupInfo.append({
                    'ID': group.id,
                    'NAME': group.name,
                    'PERMISSIONS': permissions,
                })
            data = {**data, **dict({'GROUPS': groupInfo})}
            tmp = {}
            for permission in Permissions.objects.all():
                tmp = {**tmp, **dict({permission.code: permission.name})}
            data = {**data, **dict({'PERMISSIONS': tmp})}
            data = {**data, **errorCheckMessage(True, None)}
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Delete all moodbars in the moodbar folder.
@login_required(redirect_field_name='login.html', login_url='app:login')
def removeAllMoods(request):
    if request.method == 'GET':
        user = request.user
        if checkPermission(["ADMV"], user):
            moodbars = "/ManaZeak/static/mood/"
            for mood in os.listdir(moodbars):
                os.remove(os.path.join(moodbars, mood))
            data = errorCheckMessage(True, None)
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Delete a user from an ID
@login_required(redirect_field_name='login.html', login_url='app:login')
def removeUser(request):
    if request.method == 'POST':
        user = request.user
        if checkPermission(["ADMV"], user):
            response = json.loads(request.body)
            if 'USER_ID' in response:
                try:
                    userId = int(strip_tags(response['USER_ID']))
                    if userId != user.id:
                        if User.objects.filter(id=userId).count() == 1:
                            user = User.objects.get(id=userId)
                            deleteLinkedEntities(user)
                            user.delete()
                            data = errorCheckMessage(True, None)
                        else:
                            data = errorCheckMessage(False, "dbError")
                    else:
                        data = errorCheckMessage(False, "userDeleteError")
                except ValueError:
                    data = errorCheckMessage(False, "valueError")
            else:
                data = errorCheckMessage(False, "badFormat")
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Force a syncthing rescan
@login_required(redirect_field_name='login.html', login_url='app:login')
def syncthingRescan(request):
    if request.method == 'GET':
        user = request.user
        if checkPermission(["ADMV"], user):
            headers = {'X-API-Key': AdminOptions.objects.all().first().syncthingKey}
            req = requests.post('http://st:8384/rest/db/scan', headers=headers)
            if req.status_code == 200:
                data = errorCheckMessage(True, None)
            else:
                data = errorCheckMessage(False, "syncthingError")
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Change the syncthing API key in the database
@login_required(redirect_field_name='login.html', login_url='app:login')
def changeSyncthingAPIKey(request):
    if request.method == 'POST':
        user = request.user
        if checkPermission(["ADMV"], user):
            response = json.loads(request.body)
            if 'SYNC_KEY' in response:
                adminOptions = getAdminOptions()
                syncKey = strip_tags(response['SYNC_KEY'])
                if syncKey != adminOptions.syncthingKey:
                    adminOptions.syncthingKey = syncKey
                    adminOptions.save()
                data = errorCheckMessage(True, None)
            else:
                data = errorCheckMessage(False, "badFormat")
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Change the buffer path in the database
@login_required(redirect_field_name='login.html', login_url='app:login')
def changeBufferPath(request):
    if request.method == 'POST':
        user = request.user
        if checkPermission(["ADMV"], user):
            response = json.loads(request.body)
            if 'BUFFER_PATH' in response:
                adminOptions = getAdminOptions()
                bufferPath = strip_tags(response['BUFFER_PATH'])
                if os.path.isdir(bufferPath):
                    adminOptions.bufferPath = bufferPath
                    adminOptions.save()
                    data = errorCheckMessage(True, None)
                else:
                    data = errorCheckMessage(False, "dirNotFound")
            else:
                data = errorCheckMessage(False, "badFormat")
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Delete all covers and launch a rescan for covers
@login_required(redirect_field_name='login.html', login_url='app:login')
def regenerateCovers(request):
    if request.method == 'GET':
        user = request.user
        if checkPermission(["ADMV"], user):
            # Deleting all covers
            moodbars = "/ManaZeak/static/img/covers"
            for mood in os.listdir(moodbars):
                os.remove(os.path.join(moodbars, mood))

            # Recreating covers
            scanThread = Process(target=regenerateCoverProcess)
            db.connections.close_all()
            scanThread.start()
            data = errorCheckMessage(True, None)
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Process for handling regeneration
def regenerateCoverProcess():
    tracks = Track.objects.all()
    for track in tracks:
        regenerateCover(track)


# Return the status of a user
@login_required(redirect_field_name='login.html', login_url='app:login')
def isAdmin(request):
    if request.method == 'GET':
        data = {
            'IS_ADMIN': request.user.is_superuser
        }
        data = {**data, **errorCheckMessage(True, None)}
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Drop all database
@login_required(redirect_field_name='login.html', login_url='app:login')
def dropAllDB(request):
    if request.method == 'GET':
        user = request.user
        if checkPermission(["ADMV"], user):
            # Delete views and indexes for playlists
            for playlist in Playlist.objects.all():
                deleteView(playlist)
            Track.objects.all().delete()
            Artist.objects.all().delete()
            Album.objects.all().delete()
            Playlist.objects.all().delete()
            Library.objects.all().delete()
            Genre.objects.all().delete()
            Shuffle.objects.all().delete()
            UserHistory.objects.all().delete()
            Stats.objects.all().delete()
            History.objects.all().delete()
            data = errorCheckMessage(True, None)
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


def isInviteEnabled(request):
    if request.method == 'GET':
        data = {
            'INVITE': getAdminOptions().inviteCodeEnabled
        }
        data = {**data, **errorCheckMessage(True, None)}
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Enable or disable the invitation mode
@login_required(redirect_field_name='login.html', login_url='app:login')
def toggleInvite(request):
    if request.method == 'GET':
        user = request.user
        if checkPermission(["ADMV"], user):
            adminOptions = getAdminOptions()
            adminOptions.inviteCodeEnabled = not adminOptions.inviteCodeEnabled
            adminOptions.save()
            data = {
                'INVITE': adminOptions.inviteCodeEnabled
            }
            data = {**data, **errorCheckMessage(True, None)}
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


@login_required(redirect_field_name='login.html', login_url='app:login')
def editGroup(request):
    if request.method == 'POST':
        user = request.user
        if checkPermission(["GRPE"], user):
            response = json.loads(request.body)
            # TODO: Add permission edition
            if 'GROUP_ID' in response and 'GROUP_NAME' in response and 'PERMISSIONS':
                groupId = strip_tags(response['GROUP_ID'])
                if Groups.objects.filter(id=groupId).count() == 1:
                    group = Groups.objects.get(id=groupId)
                    group.name = strip_tags(response['GROUP_NAME'])
                    group.save()
                    permissions = Permissions.objects.all()
                    for permission in permissions:
                        if permission.code not in response['PERMISSIONS']:
                            return JsonResponse(errorCheckMessage(False, "badFormat"))
                    for permission in permissions:
                        perm = response['PERMISSIONS'][permission.code]
                        if perm:
                            if group.permissions.filter(code=permission.code).count() == 0:
                                group.permissions.add(Permissions.objects.get(code=permission.code))
                        else:
                            if group.permissions.filter(code=permission.code).count() == 1:
                                group.permissions.remove(Permissions.objects.get(code=permission.code))
                    data = errorCheckMessage(True, None)
                else:
                    data = errorCheckMessage(False, "dbError")
            else:
                data = errorCheckMessage(False, "badFormat")
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


@login_required(redirect_field_name='login.html', login_url='app:login')
def editUserGroup(request):
    if request.method == 'POST':
        user = request.user
        response = json.loads(request.body)
        if checkPermission(["GAPR"], user):
            if 'GROUP_ID' in response and 'USER_ID' in response:
                userId = strip_tags(response['USER_ID'])
                groupId = strip_tags(response['GROUP_ID'])
                if User.objects.filter(id=userId).count() == 1:
                    user = User.objects.get(id=userId)
                    userPref = UserPreferences.objects.get(user=user)
                    if Groups.objects.filter(id=groupId).count() == 1:
                        userPref.group = Groups.objects.get(id=groupId)
                        userPref.save()
                        data = errorCheckMessage(True, None)
                    else:
                        data = errorCheckMessage(False, "dbError")
                else:
                    data = errorCheckMessage(False, "dbError")
            else:
                data = errorCheckMessage(False, "badFormat")
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Delete a library or a playlist depending of what has been send
@login_required(redirect_field_name='login.html', login_url='app:login')
def deleteCollection(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        user = request.user
        if 'PLAYLIST_ID' in response:
            playlistId = strip_tags(response['PLAYLIST_ID'])
            if Playlist.objects.filter(id=playlistId).count() == 1:
                playlist = Playlist.objects.get(id=playlistId)

                # Library deletion
                if playlist.isLibrary:
                    if checkPermission(["LIBR"], user):
                        if Library.objects.filter(playlist=playlist).count() == 1:
                            deleteView(playlist)
                            deleteLibrary(Library.objects.get(playlist=playlist))
                            data = errorCheckMessage(True, None)
                        else:
                            data = errorCheckMessage(False, "dbError")
                    else:
                        data = errorCheckMessage(False, "permissionError")

                # Playlist deletion
                else:
                    if playlist.user == user and checkPermission(["PLST"], user):
                        deleteView(playlist)
                        playlist.delete()
                        data = errorCheckMessage(True, None)
                    else:
                        data = errorCheckMessage(False, "permissionError")

            else:
                data = errorCheckMessage(False, "dbError")
        else:
            data = errorCheckMessage(False, "badFormat")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)


# Check if the tagging has been done correctly
@login_required(redirect_field_name='login.html', login_url='app:login')
def checkNamingConventionArtistsOnPlaylist(request):
    data = {}
    if request.method == 'POST':
        user = request.user
        if user.is_superuser:
            response = json.loads(request.body)
            if 'PLAYLIST_ID' in response:
                playlistId = response['PLAYLIST_ID']
                data = set()
                if Playlist.objects.filter(id=playlistId).count() == 1:
                    tracks = Playlist.objects.get(id=playlistId).track.all()
                    for track in tracks:
                        path, fileName = os.path.split(track.location)
                        splicedName = fileName.split(" - ")
                        # Extracting artists
                        artists = splicedName[0]
                        splicedArtists = artists.split(",")
                        # Checking if the artists are in a good order
                        for i in range(len(splicedArtists) - 1):
                            artist1 = splicedArtists[i].rstrip().lstrip()
                            artist2 = splicedArtists[i + 1].rstrip().lstrip()
                            if artist1[0] > artist2[0]:
                                data.add(track)
                                break

                        # Checking if the title contains caps at the beginning of each word
                        fileName = splicedName[1]
                        words = fileName.split(" ")
                        for word in words:
                            if not word[0].isupper():
                                data.add(track)
                                break

                        # The tracks contains a featuring
                        if "(feat." in fileName:
                            feats = fileName.split("feat.")
                            for i in range(len(feats) - 1):
                                artist1 = feats[i].rstrip().lstrip()
                                artist2 = feats[i + 1].rstrip().lstrip()
                                if artist1[0] > artist2[0]:
                                    data.add(track)
                                    break
                    data = dict({'RESULT': data})
                    data = {**data, **errorCheckMessage(True, None)}
                else:
                    data = errorCheckMessage(False, "dbError")
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)
