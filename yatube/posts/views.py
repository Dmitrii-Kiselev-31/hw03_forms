from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required


from .forms import PostForm
from .models import Post
from .models import Group, User

CUTOFF = 10
User = get_user_model()


def get_page(queryset, request):
    paginator = Paginator(queryset, CUTOFF)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }


def index(request):
    posts = Post.objects.select_related('group', 'author')
    context = {
        'posts': posts,
    }
    context = get_page(Post.objects.all(), request)
# Тут тоже не пойму как сделать
    return render(request, 'posts/index.html', context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related('author')[:CUTOFF]
    context = {
        'group': group,
        'posts': posts,
    }
    context.update(get_page(group.posts.all(), request))
    return render(request, 'posts/group_list.html', context)
# Не получается у меня без Update, по вашем предложению просидел
# Так и не разобрался не выходит, все ломается и страница пустая


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author').all()
    context = {
        'author': author,
    }
    context.update(get_page(author.posts.all(), request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_edit = True
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)
