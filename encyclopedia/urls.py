from django.urls import path

from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("<str:name>", views.entry, name="entry"),
    # path(r'^wiki/$', views.entry, name="entry"),
]
