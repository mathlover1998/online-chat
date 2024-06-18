from django.db import models
from django.contrib.auth.models import User
import shortuuid

# Create your models here.
class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128,unique=True,default=shortuuid.uuid)
    # users_online = models.ManyToManyField(User,related_name='online_in_groups',blank=True)
    members = models.ManyToManyField(User,related_name='chat_groups',blank=True)
    def __str__(self) -> str:
        return self.group_name
    
class Message(models.Model):
    group = models.ForeignKey(ChatGroup,on_delete=models.CASCADE,related_name='chat_messages')
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    body = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user} : {self.body}"
    
    class Meta:
        ordering = ['-created']