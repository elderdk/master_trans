from django.urls import path
from . import views


urlpatterns = [
    path('', views.display_landing, name='landing'),
    path('dashboard/', views.ProjectListView.as_view(), name='dashboard'),
    path('project/new', views.ProjectCreateView.as_view(), name='project-add'),

    path('project/delete/<int:pk>', views.ProjectDeleteView.as_view(),
         name='project-delete'),

    path('project/update/<int:pk>', views.ProjectUpdateView.as_view(),
         name='project-update'),

    path('project/translate/<int:pk>', views.segment_translate_view,
         name='segment-list')
]