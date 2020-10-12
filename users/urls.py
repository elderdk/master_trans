from django.urls import path
from . import views


urlpatterns = [
    path('signup', views.StudentSignUpView.as_view(), name='signup'),
]