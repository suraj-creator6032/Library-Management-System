from django.urls import path
from . import views

urlpatterns = [
    path('', views.member_login, name='member_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.member_logout, name='member_logout'),
]