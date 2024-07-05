from django.urls import path, include
from . import views

urlpatterns = [
    path('check/', views.check, name='check'),
    path('results/', views.results, name='results'),
    path('upload/', views.file_upload, name='file_upload'),
]
