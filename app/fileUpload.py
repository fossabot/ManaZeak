import base64
import json

import os

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.html import strip_tags

from app.adminTools import getAdminOptions
from app.track.importer import importTrack
from app.utils import errorCheckMessage, checkPermission


# Handle the file upload
@login_required(redirect_field_name='login.html', login_url='app:login')
def handleUploadedFile(request):
    if request.method == 'POST':
        user = request.user
        response = json.loads(request.body)
        if checkPermission(["UPLD"], user):
            if 'CONTENT' in response and 'FILENAME' in response:
                name = strip_tags(response['FILENAME'])
                if '/' not in name and '\\' not in name:
                    adminOptions = getAdminOptions()
                    if not os.path.exists(os.path.join(adminOptions.bufferPath, "TODO")):
                        try:
                            os.makedirs(os.path.join(adminOptions.bufferPath, "TODO"))
                        except os.error:
                            return JsonResponse(errorCheckMessage(False, "dNdError"))
                    filePath = os.path.join(adminOptions.bufferPath, "TODO", name)
                    if not os.path.isfile(filePath):
                        with open(filePath, 'wb+') as destination:
                            # Split the header with MIME type
                            destination.write(base64.b64decode(str(response['CONTENT'].split(",")[1])))
                        importTrack(filePath, user)
                        data = errorCheckMessage(True, None)
                    else:
                        data = errorCheckMessage(False, "fileExists")
                else:
                    data = errorCheckMessage(False, "badFileName")
            else:
                data = errorCheckMessage(False, "badFormat")
        else:
            data = errorCheckMessage(False, "permissionError")
    else:
        data = errorCheckMessage(False, "badRequest")
    return JsonResponse(data)
