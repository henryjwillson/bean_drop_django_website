from django.urls import path
from . import views
from .views import PostListView, UserPostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(),
         name='post-detail'),  # Post with the pk (primary key)
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('charity/', views.charity, name='charity'),
    path('contact_us/', views.contactView, name='contact_us'),
    path('private-policy/', views.private_policy, name='private_policy'),
    path('the-bean-drop-team/', views.the_bean_drop_team, name='the-bean-drop-team'),
    path('faqs/', views.faqs, name='faqs'),
    path('locations/', views.locations, name='locations'),
]
