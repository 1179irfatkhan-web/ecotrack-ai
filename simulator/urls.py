from django.urls import path
from .views import simulator_view

urlpatterns = [
    path('', simulator_view, name='simulator'),
]
