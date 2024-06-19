from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.http import Http404
from .models import *
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def chat_view(request,chatroom_name ='public-chat'):
    chat_group = get_object_or_404(ChatGroup,group_name=chatroom_name)
    messages = chat_group.chat_messages.all()[:30]
    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break
    #does not need anymore when using websocket
    # if request.htmx:
    #     body = request.POST.get('message')
    #     message = Message.objects.create(user=request.user,group=chat_group,body=body)
    #     context = {
    #         'message':message,
    #         'user': request.user
    #     }
    #     return render(request,'rtchat/partials/chat_message_p.html',context)
        
    context = {
        'chat_messages':messages,
        'other_user': other_user,
        'group_name': chatroom_name
    }
    return render(request,'rtchat/chat.html',context)

@login_required
def get_or_create_chatroom(request,username):
    if request.user.username == username:
        return redirect(reverse('home'))
    other_user = get_object_or_404(User,username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)
    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom = chatroom
                break
            else:
                chatroom = ChatGroup.objects.create(is_private=True)
                chatroom.members.add(other_user,request.user)
    else:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user,request.user)
    return redirect('chatroom',chatroom_name=chatroom.group_name)