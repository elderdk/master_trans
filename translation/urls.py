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
    
    path('project/review/<int:pk>', views.SegmentQAView.as_view(),
         name='segment-qa'),
     
    path('project/review/<int:pk>', views.SegmentTORView.as_view(),
         name='segment-tor'),

    path('projcet/translate/commit/<int:file_id>/<int:seg_id>',
         views.SegmentCommitView.as_view(),
         name='segment-commit'
         ),

    path('project/translate/search_match/<str:source_text>',
         views.GetDiffHtmlView.as_view(),
         name='search_match'
         ),

]