# coding: utf-8

from django.shortcuts import redirect


def login_required(view_func):
    def check(request):
        if 'uid' in request.session:
            return view_func(request)
        else:
            return redirect('/user/login/')
    return check
