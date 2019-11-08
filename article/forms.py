#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: Jamin Chen
@date:  2019/8/6 14:05
@explain: 
@file: forms.py
"""
from django import forms
from .models import ArticlePost
#写文章的表单类
class ArticlePostForm(forms.ModelForm):
    class Meta:
        #指明数据模型来源
        model = ArticlePost
        #定义表单包含的字段
        fields = ('title','body', 'tags','avatar')


