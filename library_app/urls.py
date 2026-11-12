from django.urls import path
from . import views
from django.shortcuts import render

urlpatterns = [
    path('', views.member_login, name='member_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.member_logout, name='member_logout'),
    path('tailwind-test/',lambda request: render(
        request, 'library_app/tailwind_test.html'
    )),
    path('books/',views.books_catalogue, name='books_catalogue'),
    path('books/<int:book_id>/',views.book_detail, name='book_detail'),
    path('books/add/',views.add_book, name='add_book'),
    path('books/<int:book_id>/edit/',views.edit_book, name='edit_book'),
    path('books/<int:book_id>/copies/add/',views.add_book_copies,name='add_book_copies'),
    path('reference-data/', views.reference_data, name='reference_data'),
    path('reference-data/<str:record_type>/add/', views.manage_reference ,name='add_reference'),
    path('reference-data/<str:record_type>/<int:record_id>/edit/', views.manage_reference, name='edit_reference'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('members/', views.members_directory, name='members_directory'),
    path('members/<int:member_id>/',views.member_detail, name='member_detail'),
    path('members/add/',views.add_member, name='add_member'),
    path('members/<int:member_id>/edit/', views.edit_member, name='edit_member'),
    path('members/<int:member_id>/reset-password/', views.reset_member_password, name='reset_member_password'),
    path('coming-soon/<str:section>/',views.coming_soon, name='coming_soon'),
]