from django.db import models
from django.contrib.auth.models import User

class Friendship(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendship_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendship_user2")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user1.username} と {self.user2.username} は友達です"


class FriendSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_settings')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_settings_friend')
    healthcheck_notification_enabled = models.BooleanField(default=False)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.user.username} と {self.friend.username}の設定"

class HealthcheckNotification(models.Model):
    STATUS_CHOICES = [
        ('good', '良好'),
        ('poor', '不良')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='healthcheck_notification')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.get_status_display()}"
    
# スタンプモデル
class Stamp(models.Model):
    stamp_name = models.CharField(max_length=100)
    image_path = models.ImageField(upload_to='stamps/', null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.stamp_name
    
class Chat(models.Model):
    user = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)