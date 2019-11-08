from django.contrib import admin
from .models import ArticlePost
from .models import ArticleColumn
# Register your models here.

#注册ArticlePost到admin中
admin.site.register(ArticleColumn)
admin.site.register(ArticlePost)
