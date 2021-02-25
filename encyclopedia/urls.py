from django.urls import path

from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("edit_page", views.edit_page, name="edit_page"),
    path("create_page", views.create_page, name="create_page"),
    path("<str:name>", views.entry, name="entry"),
    # path(r'^wiki/$', views.entry, name="entry"),
]
