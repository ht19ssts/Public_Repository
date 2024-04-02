# Register your models here.
from django.contrib import admin
from .models import Friendship, Stamp, FriendSettings, Chat, HealthcheckNotification

admin.site.register(Friendship)

admin.site.register(Stamp)

admin.site.register(FriendSettings)

admin.site.register(Chat)

admin.site.register(HealthcheckNotification)