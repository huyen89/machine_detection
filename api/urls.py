from django.urls import path
from api import views

urlpatterns = [
    path('api', views.index_page),
    path('predict', views.predict_mgc),
]