from django.shortcuts import render, get_object_or_404
from .models import Post
from products.models import Category
from django.db import models


# Create your views here.
def blog_view(request):
    q = request.GET.get('search', '').strip()
    categories = list(Category.objects.all().order_by('name'))
    recent_posts = list(Post.objects.filter(published=True).order_by('-date')[:3])
    for p in recent_posts:
        p.date_str = p.date.strftime('%d/%m/%Y')

    if q:
        posts_qs = Post.objects.filter(published=True).filter(
            models.Q(title__icontains=q) | models.Q(content__icontains=q) | models.Q(summary__icontains=q)
        ).order_by('-date')
        posts = list(posts_qs)
        for p in posts:
            p.date_str = p.date.strftime('%d/%m/%Y')
    else:
        posts = list(Post.objects.filter(published=True))
        for p in posts:
            p.date_str = p.date.strftime('%d/%m/%Y')

    context = {
        'posts': posts,
        'recent_posts': recent_posts,
        'categories': categories,
        'current_category': None,
        'search': q,
    }
    return render(request, 'blog/blog.html', context)


def blog_single_view(request, post_id=None):
    post = None
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
    recent_posts = list(Post.objects.filter(published=True).order_by('-date')[:3])
    if post:
        post.date_str = post.date.strftime('%d/%m/%Y')
    for p in recent_posts:
        p.date_str = p.date.strftime('%d/%m/%Y')
    categories = list(Category.objects.all().order_by('name'))
    context = {'post': post, 'recent_posts': recent_posts, 'categories': categories, 'current_category': None}
    return render(request, 'blog/blog-single.html', context)


def blog_search_view(request):
    return blog_view(request)
