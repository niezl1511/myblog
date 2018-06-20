# coding: utf-8

from urllib.parse import urlencode

import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password

from user.models import User
from user.forms import UserForm
from user.helper import login_required


def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():  # 数据验证
            # 处理密码，并创建用户
            user = form.save(commit=False)
            user.password = make_password(user.password)
            user.save()

            # 设置用户登录状态
            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname
            request.session['avatar'] = user.avatar
            return redirect('/user/info/')
        else:
            return render(request, 'register.html', {'error': form.errors})
    else:
        return render(request, 'register.html')


def login(request):
    query_string = urlencode(settings.WB_AUTH_PARAMS)
    auth_url = '%s?%s' % (settings.WB_AUTH_API, query_string)

    if request.method == 'POST':
        nickname = request.POST.get('nickname', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': '用户不存在', 'auth_url': auth_url})

        if check_password(password, user.password):
            # 设置用户登录状态
            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname
            request.session['avatar'] = user.avatar
            return redirect('/user/info/')
        else:
            return render(request, 'login.html', {'error': '密码错误，请重新输入', 'auth_url': auth_url})

    return render(request, 'login.html', {'auth_url': auth_url})


@login_required
def user_info(request):
    uid = request.session['uid']
    user = User.objects.get(id=uid)
    return render(request, 'user_info.html', {'user': user})


def logout(request):
    request.session.flush()
    return redirect('/')


def weibo_callback(request):
    # 获取 Access Token
    code = request.GET.get('code')
    access_params = settings.WB_TOKEN_PARAMS.copy()
    access_params['code'] = code
    resp = requests.post(settings.WB_TOKEN_API, data=access_params)
    access_data = resp.json()

    # 获取微博用户信息
    user_params = settings.WB_USER_SHOW_PARAMS.copy()
    user_params['access_token'] = access_data['access_token']
    user_params['uid'] = access_data['uid']
    resp = requests.get(settings.WB_USER_SHOW_API, params=user_params)
    user_data = resp.json()

    # 获取与平台账号关联的用户数据
    try:
        user = User.objects.get(openid=user_data['id'])
    except User.DoesNotExist:
        user = User.objects.create(
            nickname=user_data['name'],
            openid=user_data['id'],
            openicon=user_data['avatar_hd'],
            sex='U',
            age=18,
        )

    request.session['uid'] = user.id
    request.session['nickname'] = user.nickname
    request.session['avatar'] = user.avatar

    return redirect('/user/info/')
