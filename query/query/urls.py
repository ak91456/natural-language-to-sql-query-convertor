from django.contrib import admin
from django.urls import path
from query_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.query_view, name='query'),
]
