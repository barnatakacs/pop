from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    path('', views.ChatsListView.as_view(), name='chats'),
    path('create_chat/<int:user_id>/',
         views.CreateOrRedirectChatView.as_view(), name='create_chat'),
    path('<int:pk>/', views.ChatDetailView.as_view(), name='chat_detail')
]
