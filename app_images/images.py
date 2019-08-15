from django.urls import path
from . import views


app_name = 'app_images'

urlpatterns = [
    path('create/', views.image_create, name='create'),
]

