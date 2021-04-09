from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q, Count, Sum
from yatube.settings import PAR_PAGE

from .forms import CommentForm, PostForm, GroupForm
from .models import Follow, Group, Post, User, Comment


def index(request):
    """Главная страница."""
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'index.html', {
            'page': page,
            'index': True,
            'all_author': True,
        }
    )


@login_required
def follow_index(request):
    """Страница избранных авторов."""
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {
        'page': page,
        'paginator': paginator,
        'index': True,
    }
    )


@login_required
def profile_follow(request, username):
    """Добавление подписчика."""
    if request.user == get_object_or_404(User, username=username):
        return redirect(profile, username)
    Follow.objects.get_or_create(
        user=request.user,
        author=get_object_or_404(User, username=username)
    )
    return redirect(profile, username)


@login_required
def profile_unfollow(request, username):
    """Удаление подписки."""
    follow = Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)
    )
    follow.delete()
    return redirect(profile, username)


@login_required
def new_group(request):
    """Страница добавления группы."""
    form = GroupForm(request.POST or None)
    if not request.method == 'POST':
        return render(request, 'new_group.html', {'form': form})
    if not form.is_valid():
        return render(request, 'new_group.html', {'form': form})
    form.save()
    return redirect('all_group')


@login_required
def group_edit(request, slug):
    """Страница редактирования группы."""
    group = get_object_or_404(Group, slug=slug)
    form = GroupForm(
        request.POST or None,
        instance=group,
        initial={
            'title': group.title,
            'description': group.description,
            'slug': group.slug
        }
    )
    if form.is_valid():
        form.save()
        return redirect(group_list)
    return render(request, 'group_edit.html', {
        'group': group,
        'form': form
    }
    )


def group_posts(request, slug):
    """Страница группы."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'group.html', {
            'group': group,
            'page': page,
        }
    )


def group_list(request):
    """Страница всех групп."""

    count_group = Post.objects.values(
        'group').order_by('-count').annotate(count=Count('group'))
    total_group = []
    for group in count_group:
        if group['group'] is None:
            continue
        total_group.append(
            Group.objects.get(id=group['group']))
    # Список id групп без нулевых постов
    total_group_id = []
    for group in total_group:
        total_group_id.append(group.id)
    check = Group.objects.values('id')
    check_list = []
    for group in check:
        check_list.append(group['id'])
    result = list(set(check_list) - set(total_group_id))
    for group in result:
        total_group.append(Group.objects.get(id=group))
    # Все посты по алфавиту title.
    # total_group = Group.objects.order_by('title').all()
    return render(request, 'group_list.html', {'total_group': total_group})


def best_views(request):
    """Страница самых просматриваемых постов."""
    post_list = Post.objects.select_related('group').order_by('-views').all()
    paginator = Paginator(post_list, PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'best.html', {
            'page': page,
            'best': True,
            'best_views': True,
        }
    )


def best_comment(request):
    """Страница самых комментируемых постов."""
    count_comment = Comment.objects.values(
        'post').order_by('-count').annotate(count=Count('post'))
    post_list = []
    for comment in count_comment:
        post_list.append(
            Post.objects.select_related('group').get(id=comment['post']))
    paginator = Paginator(post_list, PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'best.html', {
            'page': page,
            'best': True,
            'best_comment': True,
        }
    )


def best_author(request):
    """Страница самого популярного автора."""
    count_author = Follow.objects.values(
        'author').order_by('-count').annotate(count=Count('author'))
    post_list = Post.objects.select_related(
        'group').filter(author=count_author[0]['author'])
    paginator = Paginator(post_list, PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'best.html', {
            'page': page,
            'best': True,
            'best_author': True,
        }
    )


def stat_author(request):
    """Страница статистики авторов."""
    labels = []
    data = []
    qs = Post.objects.values('author').order_by(
        '-count').annotate(count=Count('author'))[:5]
    for post in qs:
        labels.append(User.objects.get(id=post['author']).username)
        data.append(post['count'])
    return render(request, 'statistic.html', {
        'labels': labels,
        'data': data,
        'stat': True,
        'stat_author_nav': True,
    }
    )


def stat_view(request):
    """Страница статистики просмотра постов."""
    labels = []
    data = []
    qs = Post.objects.values(
        'author').order_by('-sum').annotate(sum=Sum('views'))[:5]
    for post in qs:
        labels.append(User.objects.get(id=post['author']).username)
        data.append(post['sum'])
    return render(request, 'statistic.html', {
        'labels': labels,
        'data': data,
        'stat': True,
        'stat_view_nav': True,
    }
    )


def stat_group(request):
    """Страница статистики групп."""
    labels = []
    data = []
    qs = Post.objects.values('group').order_by(
        '-count').annotate(count=Count('group'))[:5]
    for post in qs:
        if post['count'] == 0:
            continue
        labels.append(Group.objects.get(id=post['group']).title)
        data.append(post['count'])
    return render(request, 'statistic.html', {
        'labels': labels,
        'data': data,
        'stat': True,
        'stat_group_nav': True,
    }
    )


def stat_follow(request):
    """Страница статистики подписчиков."""
    labels = []
    data = []
    qs = Follow.objects.values('author').order_by(
        '-count').annotate(count=Count('author'))[:5]
    for post in qs:
        labels.append(User.objects.get(id=post['author']).username)
        data.append(post['count'])
    return render(request, 'statistic.html', {
        'labels': labels,
        'data': data,
        'stat': True,
        'stat_follow_nav': True,
    }
    )


def profile(request, username):
    """Страница профиля пользователя."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    # Авторизованный пользователь(подписчик) подписан на автора страницы.
    if request.user.is_authenticated:
        following: bool = Follow.objects.filter(
            author__username=username, user=request.user)
    else:
        following: bool = False

    return render(request, 'profile.html', {
        'author': author,
        'posts': posts,
        'page': page,
        'following': following,
    }
    )


def post_view(request, username, post_id):
    """Страница записи."""
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    comments = post.comments.all()

    if request.user.is_authenticated:
        following: bool = Follow.objects.filter(
            author__username=username, user=request.user)
    else:
        following: bool = False

    post.views += 1
    post.save(update_fields=['views'])
    return render(request, 'post.html', {
        'author': post.author,
        'post': post,
        'comments': comments,
        'following': following,
        'read_post': True,
    }
    )


@login_required
def new_post(request):
    """Страница добавления записи."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not request.method == 'POST':
        return render(request, 'new.html', {'form': form, 'new_post': True})
    if not form.is_valid():
        return render(request, 'new.html', {'form': form, 'new_post': True})
    post = form.save(commit=False)
    post.author = request.user
    post.views += 1
    post.save()
    return redirect('index')


def post_edit(request, username, post_id):
    """Страница редактирования поста."""
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user == post.author:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post,
            initial={'text': post.text, 'group': post.group}
        )
        if form.is_valid():
            form.save()
            return redirect(post_view, username, post_id)
        return render(request, 'new.html', {
            'post': post,
            'form': form
        }
        )
    return redirect(post_view, username, post_id)


@login_required
def add_comment(request, username, post_id):
    """Добавление комментария."""
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = post.comments.all()

    if request.user.is_authenticated:
        following: bool = Follow.objects.filter(
            author__username=username, user=request.user)
    else:
        following: bool = False

    form = CommentForm(request.POST or None)
    if not request.method == 'POST':
        return render(request, 'post.html', {
            'author': post.author,
            'post': post,
            'comments': comments,
            'form': form,
            'following': following,
            'comment': True,
        }
        )
    if not form.is_valid():
        return render(request, 'post.html', {
            'author': post.author,
            'post': post,
            'comments': comments,
            'form': form,
        }
        )
    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.save()
    return redirect(post_view, username, post_id)


def page_not_found(request, exception):
    """Страница 404."""
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    """Страница 500."""
    return render(request, 'misc/500.html', status=500)


def search(request):
    """Страница поиска по постам."""
    query = request.GET.get('q')
    page = Post.objects.select_related('group').filter(
        Q(text__contains=query.lower())
        | Q(author__username__contains=query.lower())
        | Q(group__title__contains=query.lower())
        | Q(pub_date__contains=query.lower())
    )
    # paginator = Paginator(object_list, PAR_PAGE)
    # page_number = request.GET.get('page')
    # search_url = '?q=%s' % query
    # page = paginator.get_page(page_number)
    return render(request, 'search.html', {
        'page': page,
        'query': query,
    }
    )
