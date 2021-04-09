from django.urls import path

from . import views
# from .views import SearchResultsView

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path(
        'best_views/',
        views.best_views,
        name='best_views'
    ),
    path(
        'best_comment/',
        views.best_comment,
        name='best_comment'
    ),
    path(
        'best_author/',
        views.best_author,
        name='best_author'
    ),
    path('stat_view/', views.stat_view, name='stat_view'),
    path('stat_group/', views.stat_group, name='stat_group'),
    path('stat_author/', views.stat_author, name='stat_author'),
    path('stat_follow/', views.stat_follow, name='stat_follow'),
    path('group/', views.group_list, name='all_group'),
    path('group/<slug:slug>/', views.group_posts, name='page_group'),
    path('new_group/', views.new_group, name='new_group'),
    path('group/<slug:slug>/edit', views.group_edit, name='group_edit'),
    path('new/', views.new_post, name='new_post'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        '<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        '<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path(
        '<str:username>/<int:post_id>/edit/',
        views.post_edit,
        name='post_edit'
    ),
    path(
        '<str:username>/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
]
