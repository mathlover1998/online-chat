from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from .models import *
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def chat_view(request):
    chat_group = get_object_or_404(ChatGroup,group_name='public-chat')
    messages = chat_group.chat_messages.all()[:30]
    if request.htmx:
        body = request.POST.get('message')
        message = Message.objects.create(user=request.user,group=chat_group,body=body)
        context = {
            'message':message,
            'user': request.user
        }
        return render(request,'rtchat/partials/chat_message_p.html',context)
    return render(request,'rtchat/chat.html',{'chat_messages':messages})


def get_or_create_chatroom(request):
    pass