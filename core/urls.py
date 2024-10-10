from django.urls import path
from . import views
from .views import CustomLoginView, custom_logout
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
]
