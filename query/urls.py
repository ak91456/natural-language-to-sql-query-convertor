from django.contrib import admin
from django.urls import path
from query_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.connect_view, name="connect"),
    path("query/", views.query_view, name="query"),
    path("disconnect/", views.disconnect_view, name="disconnect"),
]
