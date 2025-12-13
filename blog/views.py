from django.shortcuts import render


# Create your views here.
def blog_view(request):
    context = {}
    return render(request, 'blog/blog.html', context)


def blog_single_view(request):
    context = {}
    return render(request, 'blog/blog-single.html', context)
