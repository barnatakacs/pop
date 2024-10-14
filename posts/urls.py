from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('new/', views.NewPostView.as_view(), name='new'),
    path('like/<int:pk>/<str:redirection>/', views.like, name='like'),
    path('delete_comment/<int:post_pk>/<int:comment_pk>/<str:redirection>/',
         views.DeleteCommentView.as_view(), name='delete_comment'),
    path('explore/', views.ExplorePageView.as_view(), name='explore'),
    path('detail/<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    path('saved/', views.SavedPageView.as_view(), name='saved'),
    path('save/<int:pk>/<str:redirection>/', views.save, name='save'),
    path('delete/<int:pk>/', views.DeletePostView.as_view(), name='delete_post')
]
