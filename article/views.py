from django.shortcuts import render,redirect
from django.http import HttpResponse
# Create your views here.
from .models import ArticlePost
import markdown
from .forms import ArticlePostForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from .models import ArticleColumn
# 引入评论表单
from comment.forms import CommentForm

def article_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    # 初始化查询集
    article_list = ArticlePost.objects.all()

    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')


    #每页显示1篇文章
    paginator = Paginator(article_list,3)
    #获取url中的页码
    page = request.GET.get('page')
    #讲导航对象相应的页码内容返回给articles
    articles = paginator.get_page(page)
    print(articles)
    #需要传递给模板（templates）的对象
    context = {'articles':articles,'order':order,'search': search,'column': column,
        'tag': tag,}
    #render函数：载入模板，并返回context对象
    return render(request,'article/list.html',context)


def article_detail(request,id):
    article = ArticlePost.objects.get(id=id)
    comments = Comment.objects.filter(article=id)
    article.total_views +=1
    article.save(update_fields=['total_views'])

    #将markdown语法渲染成html样式
    md = markdown.Markdown(
        extensions=[
            #包含 缩写、表格等常用拓展
            'markdown.extensions.extra',
            #语法高亮扩展
            'markdown.extensions.codehilite',
            # 目录扩展
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)
    comment_form = CommentForm()

    context = {'article':article,'toc':md.toc,'comments': comments ,'comment_form':comment_form}
    return render(request,'article/detail.html',context)

#写文章的视图
@login_required(login_url='/userprofile/login/')
def article_create(request):
    if request.method == 'POST':
        #将提交的数据赋值到表单实
        article_post_form = ArticlePostForm(request.POST,request.FILES)
        #判断是否符合表单格式
        if article_post_form.is_valid():
            #保存数据，但是暂时不提交
            new_article = article_post_form.save(commit=False)
            #指定数据库中id=1的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            #讲新文章保存到数据库中
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id = request.POST['column'])
            new_article.save()
            # 新增代码，保存 tags 的多对多关系
            article_post_form.save_m2m()
            #返回文章列表
            return redirect('article:article_list')
        else:
            return HttpResponse('表单内容有误，请重新填写！')
    #如果用户请求获取数据
    else:
        article_post_form= ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article_post_form':article_post_form,'columns':columns}
        return render(request,'article/create.html',context)


def article_delete(request, id):
    #根据Id获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    if request.user != article:
        return HttpResponse('抱歉，你无权修改这篇文章！')
    #调用delete方法删除文章
    article.delete()
    return redirect('article:article_list')


@login_required(login_url='/userprofile/login/')
def article_update(request,id):
    article = ArticlePost.objects.get(id=id)
    #过滤非作者用户
    if request.user != article.author:
        return HttpResponse('抱歉，你无权修改这篇文章！')
    if request.method =='POST':
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id= request.POST['column'])
            else:
                article.column =None

            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')
            #特别注意tags的更改方式不同，调用专用API
            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            return redirect('article:article_detail',id=id)
        else:
            return HttpResponse('表单内容有误，请重新填写。')
    else:
        article_post_form =ArticlePostForm()
        columns = ArticleColumn.objects.all()

        context={'article':article,'artcle_post_form':article_post_form, 'columns':columns,'tags': ','.join([x for x in article.tags.names()])}
        return render(request,'article/update.html',context)