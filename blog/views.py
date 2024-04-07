from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages

from .models import *
from .forms import *


def index(request):
    categories = Category.objects.all()
    articles = Article.objects.all()

    context = {
        'title': 'Main page',
        'categories': categories,
        'articles': articles
    }

    return render(request, 'blog/index.html', context)


def category_page_view(request, category_id):
    articles = Article.objects.filter(category=category_id).order_by('-created_at')
    categories = Category.objects.all()

    context = {
        'title': f'Категория: {Category.objects.get(id=category_id)}',
        'articles': articles,
        'categories': categories
    }

    return render(request, 'blog/category_page.html', context)


def about_me_page(request):
    return render(request, 'blog/about_me_page.html')


def works_page(request):
    return render(request, 'blog/works_page.html')


def article_detail_page_view(request, article_id):
    article = Article.objects.get(id=article_id)
    last_articles = Article.objects.all().order_by('-created_at')
    comments = Comment.objects.filter(article=article_id).order_by('-created_at')

    if article.author != request.user:
        article.views += 1
        article.save()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
    if request.method == 'GET':
        form = CommentForm()

    context = {
        'title': f'{article.title}',
        'article': article,
        'last_articles': last_articles,
        'comments': comments,
        'form': form
    }

    return render(request, 'blog/article_detail.html', context)


@login_required(login_url='login')
def add_article_view(request):
    if request.method == 'POST':
        form = AddArticleForm(data=request.POST,
                              files=request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article added successfully!')
            return redirect('article_detail', article.pk)
        else:
            for field in form.errors:
                messages.error(request, form.errors[field.as_text()])
            return redirect('add_article')

    elif request.method == 'GET':
        form = AddArticleForm()

    context = {
        'title': 'Add article',
        'form': form
    }

    return render(request, 'blog/add_article.html', context)


def register_user(request):
    if request.method == 'POST':
        form = RegisterUser(data=request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registered successfully!')
            profile_user = Profile.objects.create(user=user)
            profile_user.save()
            login(request, user)
            return redirect('index')
        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text())
            return redirect('register')
    else:
        form = RegisterUser()

    context = {
        'title': 'User registration',
        'form': form
    }

    return render(request, 'blog/register_user.html', context)


def log_in_user(request):
    if request.method == 'POST':
        form = LoginUser(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                messages.info(request, 'Logged in!')
                return redirect('index')
            else:
                messages.error(request, 'Login or password is incorrect. Try again!')
                return redirect('login')
        else:
            messages.error(request, 'Login or password is incorrect. Try again!')
            return redirect('login')
    else:
        form = LoginUser()

    context = {
        'title': 'User registration',
        'form': form
    }

    return render(request, 'blog/login.html', context)


@login_required(login_url='login')
def log_out_user(request):
    logout(request)
    messages.info(request, 'Logged out!')
    return redirect('index')


def search(request):
    word = request.GET.get('q')

    categories = Category.objects.all()
    articles = Article.objects.filter(
        title__iregex=word
    )

    context = {
        'title': 'Results of searching:',
        'categories': categories,
        'articles': articles
    }

    return render(request, 'blog/index.html', context)


@login_required(login_url='login')
def article_edit(request, article_id):
    article = Article.objects.get(id=article_id)

    if request.method == 'POST':
        form = AddArticleForm(instance=article, data=request.POST, files=request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Details updated successfully!')
            return redirect('article_detail', article.id)
        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text())
            return redirect('update_article', article.id)
    else:
        form = AddArticleForm(instance=article)

    context = {
        'form': form,
        'title': 'Edit an article'
    }

    return render(request, 'blog/add_article.html', context)


@login_required(login_url='login')
def article_delete(request, article_id):
    article = Article.objects.get(id=article_id)

    if request.method == 'POST':
        article.delete()
        messages.warning(request, 'Article deleted successfully!')

        return redirect('index')

    context = {
        'article': article,
        'title': 'Delete an article'
    }

    return render(request, 'blog/delete_article.html', context)


def profile(request, user_id):
    user = User.objects.get(id=user_id)
    profile_user = Profile.objects.get(user=user)
    articles = Article.objects.filter(author=user_id).order_by('-views')[:6]

    context = {
        'title': 'Your profile',
        'user': user,
        'profile': profile_user,
        'articles': articles
    }

    return render(request, 'blog/profile.html', context)


def edit_profile(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        user_form = UserForm(instance=user,
                             data=request.POST)
        profile_form = ProfileForm(instance=profile,
                                   data=request.POST,
                                   files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Updated successfully!')
            return redirect('user_profile', user.id)
        else:
            for field in user_form.errors:
                messages.error(request, user_form.errors[field].as_text())
            for field in profile_form.errors:
                messages.error(request, profile_form.errors[field].as_text())
            return redirect('edit_profile', user.id)
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'title': 'Edit profile',
        'profile_form': profile_form,
        'user_form': user_form
    }

    return render(request, 'blog/edit_profile.html', context)


def about_site(request):
    return render(request, 'blog/about.html')


# UNDER DEVELOPMENT
# UPD: cancelled

# @login_required(login_url='login')
# def followers_system(request, user_id):
#     followed_user = Profile.objects.get(id=user_id)
#     follower = request.user
#
#     if follower != followed_user:
#         obj, created = Profile.objects.get_or_create(follower=follower, followed_user=followed_user)
#         if not created:
#             obj.delete()
#
#     context = {
#         'title': 'Your profile',
#         'followed_user': followed_user,
#         'follower': follower
#     }
#
#     return redirect(request, 'blog/profile.html', context)


@login_required(login_url='login')
def nudges(request, article_id):
    article = Article.objects.get(id=article_id)

    if article.author == request.user:
        messages.info(request, 'Sorry, you cannot nudge your own article :(')

    else:
        article.nudges += 1
        article.save()

    context = {
        'title': f'{article.title}',
        'article': article
    }

    return render(request, 'blog/article_detail.html', context)






