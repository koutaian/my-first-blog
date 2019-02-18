from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import Post
from .forms import PostForm
from . import stock
import pandas as pd

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {"posts": posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

def analysis(request):
    if request.method == "POST":
        code = request.POST.get("code")
        codes = [code]
        mk_idx = request.POST.get("mk_idx")
        if mk_idx != "no_market":
            codes = stock.get_market_codes(mk_idx)
        year = request.POST.get("year")
        col_list = [request.POST.get("col{}".format(i)) for i in range(2) if request.POST.get("col{}".format(i))]
        df = stock.get_multiple_data(codes, col_list, year)
        table = df.to_html()
        return render(request, 'blog/analysis.html', {"table": table})
    return render(request, 'blog/analysis.html')
