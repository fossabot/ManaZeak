# Check if all the fields are present for the suggestion acceptation
def checkIfAllFields(response):
    if 'TITLE' not in response \
            and 'ARTISTS' not in response \
            and 'PERFORMER' not in response \
            and 'COMPOSER' not in response \
            and 'YEAR' not in response \
            and 'TRACK_NUMBER' not in response \
            and 'BPM' not in response \
            and 'LYRICS' not in response \
            and 'COMMENT' not in response \
            and 'GENRE' not in response \
            and 'COVER' not in response \
            and 'ALBUM_TITLE' not in response \
            and 'ALBUM_TOTAL_DISC' not in response \
            and 'DISC_NUMBER' not in response \
            and 'ALBUM_TOTAL_TRACK' not in response:
        return False
    else:
        return True


# Update the suggestion for taking only the fields accepted by the reviewer
def updateSuggestionBeforeAccept(response, suggestion):
    if not response['TITLE']:
        suggestion.title = None
    if not response['ARTISTS']:
        suggestion.artist = None
    if not response['PERFORMER']:
        suggestion.performer = None
    if not response['COMPOSER']:
        suggestion.composer = None
    if not response['YEAR']:
        suggestion.year = None
    if not response['TRACK_NUMBER']:
        suggestion.number = None
    if not response['BPM']:
        suggestion.bpm = None
    if not response['LYRICS']:
        suggestion.lyrics = None
    if not response['COMMENT']:
        suggestion.comment = None
    if not response['GENRE']:
        suggestion.genre = None
    if not response['COVER']:
        suggestion.coverLocation = None
    if not response['ALBUM_TITLE']:
        suggestion.album = None
    if not response['ALBUM_TOTAL_DISC']:
        suggestion.albumTotalDisc = None
    if not response['DISC_NUMBER']:
        suggestion.discNumber = None
    if not response['ALBUM_TOTAL_TRACK']:
        suggestion.albumTotalTrack = None
    suggestion.save()
