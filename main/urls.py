
from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('download/pdf/<str:case>/<str:language>/', views.download_pdf_view, name='download_pdf'),

]
