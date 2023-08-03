from django.urls import path
from . import views
#urlpatterns хранит в себе адреса перехода
urlpatterns = [
    path('', views.index),
    path('calculate',views.calculate)
]
