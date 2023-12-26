from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from .models import UserProfile, TaskChangeRequest

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=TaskChangeRequest)
def notification_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        # Use the 'new_user' field to get the user's ID
        user_group_name = f'user_{instance.new_user.id}' 
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                "type": "send_notification",
                "message": instance.task_title
            }
        )
   

