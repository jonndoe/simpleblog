"""common_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

# this is bad hook , it should be fixed later....
# because after password reset, it didn't go back to login page....
#from pages.views import HomePageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('app_users.urls')),
    path('users/', include('django.contrib.auth.urls')),
    path('blog/', include('app_blog.urls', namespace='blog')),
    #this is home page common for all apps.....
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('images/', include('app_images.urls', namespace='images')),
    path('course/', include('app_courses.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # this is to upload users media files i.e. images etc.
