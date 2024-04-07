from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Friendship
from .models import FriendSettings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import HealthcheckNotification
from .models import Chat, Stamp
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
import json
from collections import OrderedDict

def index(request):
    return render(request, 'MyPortfolio/index.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'myapp/signup.html', {'form': form})


@login_required
def home(request):
     context = {
        'current_time': timezone.now(),
    }
     return render(request, 'myapp/home.html', context)

def top(request):
    return render(request, 'myapp/top.html')

@login_required
def chat_with_friend(request, friend_id):
    friend = User.objects.get(pk=friend_id)
    stamps = Stamp.objects.all()
    messages = Chat.objects.filter(
        user=request.user, friend=friend
    ) | Chat.objects.filter(
        user=friend, friend=request.user
    )
    messages = messages.order_by('-created_at')
    
    friend_settings = FriendSettings.objects.filter(user=request.user, friend=friend).first()
    nickname = friend_settings.nickname if friend_settings else friend.username
    
    return render(request, 'myapp/chat.html', {
        'friend': friend,
        'nickname': nickname,
        'stamps': stamps,
        'messages': messages,
        'friend_id': friend_id
    })

@require_POST
@login_required
def send_stamp(request):
    
    data = json.loads(request.body.decode('utf-8'))
    stamp_id = int(data.get('stamp_id')) 
    friend_id = int(data.get('friend_id')) 
    
    try:
        stamp = Stamp.objects.get(id=stamp_id)
        friend = User.objects.get(id=friend_id)
        Chat.objects.create(user=request.user, friend=friend, stamp=stamp)
        return JsonResponse({"success": True, "message": "スタンプを送信しました！"})
    except Stamp.DoesNotExist:
        return JsonResponse({"success": False, "message": "指定されたスタンプは存在しません。"})
    except User.DoesNotExist:
        return JsonResponse({"success": False, "message": "指定されたユーザーは存在しません。"})

@login_required
def chat_list(request):
    received_messages = Chat.objects.filter(friend=request.user).order_by('-created_at')

    chats = {}
    for message in received_messages:
        if message.user not in chats:
            chats[message.user] = message

    chat_list_with_nickname = []
    for user, message in chats.items():

        friend_settings = FriendSettings.objects.filter(user=request.user, friend=user).first()
        nickname = friend_settings.nickname if friend_settings and friend_settings.nickname else user.username
        chat_list_with_nickname.append({
            'user': user, 
            'message': message, 
            'nickname': nickname 
        })

    sorted_chats_with_nickname = sorted(chat_list_with_nickname, key=lambda k: k['message'].created_at, reverse=True)
    
    return render(request, 'myapp/chat_list.html', {'chats': sorted_chats_with_nickname})

@login_required
def friend_list(request):
    settings = FriendSettings.objects.filter(user=request.user)
   
    friends_with_nickname = [{
        'friend': setting.friend,
        'display_name': setting.nickname if setting.nickname else setting.friend.username
    } for setting in settings]
    return render(request, 'myapp/friend_list.html', {'friends_with_nickname': friends_with_nickname})

@login_required
def notify_list(request):
    if request.method == 'POST':
        selected_friends = request.POST.getlist('notify')
        all_settings = FriendSettings.objects.filter(user=request.user)

        for setting in all_settings:
            setting.healthcheck_notification_enabled = str(setting.friend.id) in selected_friends
            setting.save()

        messages.success(request, "通知者設定を更新しました。")
        return redirect('notify_list')

    friends_with_status = OrderedDict()

    all_settings = FriendSettings.objects.filter(user=request.user)
    for setting in all_settings:
        friend_id = setting.friend.id
        nickname = setting.nickname if setting.nickname else setting.friend.username
        if friend_id not in friends_with_status:
            friends_with_status[friend_id] = {
                'friend': setting.friend,
                'nickname': nickname,
                'healthcheck_notification_enabled': setting.healthcheck_notification_enabled
            }

    context = {'friends_with_status': friends_with_status.values()}
    print(friends_with_status)
    return render(request, 'myapp/notify_list.html', context)

@login_required
def update_friend(request, friend_id):
    
    try:
        friend = User.objects.get(pk=friend_id)
    except User.DoesNotExist:
        messages.error(request, "指定されたフレンドは存在しません。")
        return redirect('friend_list')

    friend_settings = None
    try:
        friend_settings = FriendSettings.objects.get(user=request.user, friend=friend)
    except FriendSettings.DoesNotExist:
    
        messages.error(request, "フレンド設定が見つかりません。")
        return redirect('friend_list')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update':

            nickname = request.POST.get('nickname', '')
            friend_settings.nickname = nickname
            friend_settings.save()
            messages.success(request, "ニックネームを変更しました。")

        elif action == 'delete':
        
            Friendship.objects.filter(user1=request.user, user2=friend).delete()
            Friendship.objects.filter(user1=friend, user2=request.user).delete()
            FriendSettings.objects.filter(user=request.user, friend=friend).delete()
            FriendSettings.objects.filter(user=friend, friend=request.user).delete()
            messages.success(request, 'フレンドを削除しました。')
            return redirect('friend_list')

    context = {'friend': friend, 'friend_settings': friend_settings}
    return render(request, 'myapp/update_friend.html', context)

@login_required
def add_friend(request):
    users = None
    search_query = request.GET.get('search_query', '')
    message = None

    if search_query:
        users = User.objects.filter(Q(username__icontains=search_query) | Q(id__icontains=search_query))
        if not users.exists():
            messages.error(request, "指定されたユーザーは存在しません。")
            
            if request.method == 'GET':
                return redirect('add_friend')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        notify_setting = 'notify_setting' in request.POST
        target_user = User.objects.filter(id=user_id).first()
        current_user = request.user

        if target_user:
            if current_user != target_user and not FriendSettings.objects.filter(user=current_user, friend=target_user).exists():
                FriendSettings.objects.create(user=current_user, friend=target_user, healthcheck_notification_enabled=notify_setting)
                FriendSettings.objects.create(user=target_user, friend=current_user, healthcheck_notification_enabled=False)
                messages.success(request, f"{target_user.username}をフレンドに追加しました。")
                if notify_setting:
                    messages.info(request, f"{target_user.username}を通知者に設定しました。")
            elif current_user == target_user:
                messages.error(request, "自分自身をフレンドに追加することはできません。")
            else:
                messages.info(request, "既にフレンド登録されています。")

    context = {'users': users, 'messages': messages.get_messages(request)}
    return render(request, 'myapp/add_friend.html', context)


@login_required
def report_healthcheck_notification(request):
    GOOD_CONDITION_STAMP_ID = 23  # 「良好」を表すスタンプID
    POOR_CONDITION_STAMP_ID = 24  # 「不良」を表すスタンプID
    
    status = request.POST.get('status')

    HealthcheckNotification.objects.create(user=request.user, status=status)
    
    stamp_id = GOOD_CONDITION_STAMP_ID if status == 'good' else POOR_CONDITION_STAMP_ID
    stamp = Stamp.objects.get(id=stamp_id)

    unique_friend_ids = set()

    notify_settings = FriendSettings.objects.filter(
        Q(user=request.user, healthcheck_notification_enabled=True) |
        Q(friend=request.user, healthcheck_notification_enabled=True)
    )

    for setting in notify_settings:
        friend_id = setting.friend_id if setting.user == request.user else setting.user_id
        unique_friend_ids.add(friend_id)

    for friend_id in unique_friend_ids:
        friend = User.objects.get(id=friend_id)
        
        Chat.objects.create(user=request.user, friend=friend, stamp=stamp)

    return JsonResponse({"success": True, "message": "体調が報告されました。"})