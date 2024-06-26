from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('api.urls')),
    path('check/', views.check, name='check'),
    path('results/', views.results, name='results'),
]