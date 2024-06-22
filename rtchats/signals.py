from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import ChatGroup

@receiver(post_migrate)
def create_initial_groupchat(sender, **kwargs):
    if sender.name == 'rtchats':  # Replace with your actual app name
        if not ChatGroup.objects.exists():
            ChatGroup.objects.create(group_name='public-chat')
            