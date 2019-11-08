#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: Jamin Chen
@date:  2019/8/7 10:15
@explain: 
@file: urls.py
"""
from django.urls import path
from . import views
# 正在部署的应用的名称
app_name = 'userprofile'

urlpatterns = [
    path('login/',views.user_login ,name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.user_register, name='user_register'),
    path('delete/<int:id>/', views.user_delete, name='delete'),
    path('edit/<int:id>/', views.profile_edit, name='edit'),
]
