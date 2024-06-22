from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.http import Http404
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.
@login_required
def chat_view(request,chatroom_name ='public-chat'):
    chat_group = get_object_or_404(ChatGroup,group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break
    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            if request.user.emailaddress_set.filter(verified=True).exists():
                chat_group.members.add(request.user)
            else:
                messages.warning(request,"You need to verify your email to join the chat!")
    
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
        'chat_messages':chat_messages,
        'other_user': other_user,
        'group_name': chatroom_name,
        'chat_group':chat_group
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

@login_required
def create_groupchat(request):
    if request.method =='POST':
        groupchat_name = request.POST.get("groupchat_name")
        new_groupchat = ChatGroup.objects.create(admin=request.user,groupchat_name = groupchat_name)
        new_groupchat.members.add(request.user)
        # context = {
        #     'message': 
        # }
        return redirect('chatroom',new_groupchat.group_name)
    return render(request,'rtchat/create_groupchat.html')

@login_required
def chatroom_edit_view(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup,group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    if request.method =='POST':
        chat_group.groupchat_name = request.POST.get('groupchat_name')
        chat_group.save()
        remove_members = request.POST.getlist('remove_members')
        for member_id in remove_members:
            member = User.objects.get(id = member_id)
            chat_group.members.remove(member)
            channel_layer = get_channel_layer()
            user_channels = UserChannel.objects.filter(member=member, group=chat_group)
            for user_channel in user_channels:
                        async_to_sync(channel_layer.group_discard)(
                                    chatroom_name,
                                    user_channel.channel
                    )
            user_channel.delete()
        return redirect('chatroom',chatroom_name)
        
    return render(request,'rtchat/chatroom_edit.html',{'chat_group':chat_group})

@login_required
def chatroom_delete_view(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup,group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    if request.method=='POST':
        chat_group.delete()
        messages.success(request,'Chatroom deleted')
        return redirect(reverse('home'))
    
    return render(request,'rtchat/chatroom_delete.html',{'chat_group':chat_group})

@login_required
def chatroom_leave_view(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup,group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()
    if chat_group.admin == request.user:
        chat_group.admin = chat_group.members.exclude(id=request.user.id).first()
    chat_group.members.remove(request.user)
    if chat_group.members.count() == 1:
        chat_group.delete()
    messages.success(request,'You left the Chat')
    return redirect(reverse('home'))