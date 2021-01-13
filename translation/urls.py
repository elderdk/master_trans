from django.urls import path
from .views import views
from .views.project import views as pjviews
from .views.segment import views as sgviews


urlpatterns = [
    path('', views.display_landing, name='landing'),

    path('search_match/<int:file_id>/<str:seg_id>',
         views.GetDiffHtmlView.as_view(),
         name='search_match'),

    path('generate_target/<int:file_id>',
         views.GenerateTargetView.as_view(),
         name='generate_target'),
]

# Project views
urlpatterns += [
    path('dashboard/', pjviews.ProjectListView.as_view(), name='dashboard'),
    path('project/new/', pjviews.ProjectCreateView.as_view(),
         name='project-create'),

    path('project/delete/<int:pk>', pjviews.ProjectDeleteView.as_view(),
         name='project-delete'),

    path('project/update/<int:pk>', pjviews.ProjectUpdateView.as_view(),
         name='project-update'),

    path('project/delete_all/', pjviews.ProjectDeleteAllView.as_view(),
         name='project-delete-all'),
]

# Segment views
urlpatterns += [
     path('project/translate/<int:pk>', sgviews.SegmentTranslateView.as_view(),
          name='segment-translate'),

     path('project/review/<int:pk>', sgviews.SegmentReviewView.as_view(),
          name='segment-review'),

     path('project/sign-off/<int:pk>', sgviews.SegmentSOView.as_view(),
          name='segment-so'),

     path('commit/<int:file_id>/<int:seg_id>/<str:commit_token>',
          sgviews.SegmentCommitView.as_view(),
          name='segment-commit'),
]