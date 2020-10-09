from django.urls import path
from . import views


urlpatterns = [
    path('', views.StudentSignUpView.as_view(), name='signup'),
]