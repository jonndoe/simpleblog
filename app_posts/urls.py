from django.urls import path
from . import views


urlpatterns = [
    path('mine/',views.ManagePostListView.as_view(),name='manage_post_list'),
    path('create/',views.PostCreateView.as_view(),name='post_create'),
    path('<pk>/edit/',views.PostUpdateView.as_view(),name='post_edit'),
    path('<pk>/delete/',views.PostDeleteView.as_view(),name='post_delete'),


    path('post/<int:post_id>/content/<model_name>/create/',views.ContentCreateUpdateView.as_view(),
         name='post_content_create'),
    path('post/<int:post_id>/content/<model_name>/<id>/', views.ContentCreateUpdateView.as_view(),
         name='post_content_update'),

    path('content/<int:id>/delete/',views.ContentDeleteView.as_view(), name='post_content_delete'),
    path('post/<int:post_id>/', views.PostContentListView.as_view(), name='post_content_list'),

    path('content/order/', views.ContentOrderView.as_view(), name='content_order'),
]
