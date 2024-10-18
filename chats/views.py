from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Chat, User, Message

# Create your views here.


class ChatsListView(ListView):
    model = Chat
    template_name = 'chats/chats.html'
    context_object_name = 'chats'

    def get_queryset(self):
        return self.request.user.chats.all()


class CreateOrRedirectChatView(View):
    def post(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)

        chat = Chat.objects.filter(users=request.user).filter(
            users=target_user).first()

        if chat:
            return redirect('chats:chat_detail', pk=chat.id)
        else:
            chat = Chat.objects.create()
            chat.users.add(request.user, target_user)
            chat.save()

            return redirect('chats:chat_detail', pk=chat.id)


class ChatDetailView(DetailView):
    model = Chat
    template_name = 'chats/chat_detail.html'

    def get_object(self):
        chat_id = self.kwargs.get('pk')
        return get_object_or_404(Chat, id=chat_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = Message.objects.filter(
            chat=self.object).order_by('created_at')
        return context
