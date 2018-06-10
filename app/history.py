from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from app.errors import ErrorEnum, errorCheckMessage
from app.models import History, UserHistory
from app.utils import checkPermission


# Add a song to history
def addToHistory(track, user):
    history = History()
    history.track = track
    history.save()
    if UserHistory.objects.filter(user=user).count() == 0:
        userHistory = UserHistory(user=user)
        userHistory.save()
        userHistory.histories.add(history)
    # Adding to existing history
    else:
        userHistory = UserHistory.objects.get(user=user)
        userHistory.save()
        userHistory.histories.add(history)


# Get the last song played by a user
@login_required(redirect_field_name='login.html', login_url='app:login')
def getLastSongPlayed(request):
    if request.method == 'GET':
        user = request.user
        if checkPermission(["PLAY"], user):
            if UserHistory.objects.filter(user=user).count() != 0:
                userHistory = UserHistory.objects.get(user=user)
                if userHistory.histories.count() != 0:
                    trackId = 0
                    for history in userHistory.histories.order_by('-date'):
                        trackId = history.track.id
                        history.delete()
                        break
                    data = {
                        'TRACK_ID': trackId,
                    }
                    data = {**data, **errorCheckMessage(True, None, getLastSongPlayed)}
                else:
                    data = errorCheckMessage(False, ErrorEnum.NO_HISTORY, getLastSongPlayed, user)
            else:
                data = errorCheckMessage(False, ErrorEnum.NO_HISTORY, getLastSongPlayed, user)
        else:
            data = errorCheckMessage(False, ErrorEnum.PERMISSION_ERROR, getLastSongPlayed, user)
    else:
        data = errorCheckMessage(False, ErrorEnum.BAD_REQUEST, getLastSongPlayed)
    return JsonResponse(data)
