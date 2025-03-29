from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('login', google_auth_start, name='google_auth_start'),
    path('refresh', google_auth_refresh, name='google_auth_refresh'),
    path('google/login/callback/', google_auth_callback, name='google_auth_callback'),
    path("logout/", logout_view, name="logout"),
    path("drive/upload/", upload_to_drive, name="upload_to_drive"),
    path("drive/files/", list_drive_files, name="list_drive_files"),
    path("drive/download/<str:file_id>/", download_from_drive, name="download_from_drive"),
]
