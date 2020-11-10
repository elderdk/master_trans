from django.urls import path
from . import views


urlpatterns = [
    path('', views.display_landing, name='landing'),
    path('dashboard/', views.ProjectListView.as_view(), name='dashboard'),
    path('project/new', views.ProjectCreateView.as_view(),
         name='project-create'),

    path('project/delete/<int:pk>', views.ProjectDeleteView.as_view(),
         name='project-delete'),

    path('project/update/<int:pk>', views.ProjectUpdateView.as_view(),
         name='project-update'),

    path('project/translate/<int:pk>', views.SegmentTranslateView.as_view(),
         name='segment-translate'),
         
    path('project/review/<int:pk>', views.SegmentReviewView.as_view(),
         name='segment-review'),
         
    path('project/sign-off/<int:pk>', views.SegmentSOView.as_view(),
         name='segment-so'),

    path('commit/<int:file_id>/<int:seg_id>/<str:commit_token>',
         views.SegmentCommitView.as_view(),
         name='segment-commit'),

    path('search_match/<str:source_text>',
         views.GetDiffHtmlView.as_view(),
         name='search_match'),

    path('generate_target/<int:file_id>',
         views.GenerateTargetView.as_view(),
         name='generate_target'),
]
