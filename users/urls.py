from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('edit/', views.EditProfileView.as_view(), name='edit'),
    path('<str:username>/', views.ProfilePageView.as_view(), name='profile'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('<str:username>/<str:stat>/',
         views.FollowStatView.as_view(), name='follow_stat'),
]
