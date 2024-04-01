from django.shortcuts import render
from django.http import FileResponse, HttpResponse
import os
from django.conf import settings


# Create your views here.
def index(request):
    return render(request, 'liveData.html', {})


def admin_login(request):
    # Logic to handle the request, if needed
    return render(request, 'admin_login.html')


def serve_media_file(request):
    media_directory = 'files'
    file_name = str(172) + ".jpg"
    file_path = os.path.join(settings.MEDIA_ROOT, media_directory, file_name)
    with open(file_path, 'rb') as file:
        return HttpResponse(file.read(), content_type='image/jpeg')
