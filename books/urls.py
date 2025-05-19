from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('load/', views.load_book, name='load_book'),
    path('', views.list_books, name='list_books'),
    path('book/<int:book_id>/', views.view_book, name='view_book'),
    path('chapter/<int:chapter_id>/edit/', views.edit_chapter, name='edit_chapter'),
    path('book/<int:book_id>/glossary/', views.manage_glossary, name='manage_glossary'),
    path('glossary/<int:glossary_id>/delete/', views.delete_glossary, name='delete_glossary'),
    path('glossary/<int:glossary_id>/update/', views.update_glossary, name='update_glossary'),
    path('book/<int:book_id>/save/', views.save_book, name='save_book'),
    path('chapter/<int:chapter_id>/translate/', views.translate_chapter, name='translate_chapter'),
    path('book/<int:book_id>/translate/', views.translate_book, name='translate_book'),
] 