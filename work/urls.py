from django.urls import path
from . import views

urlpatterns = [
    # Writer
    path('board/',                       views.JobBoardView.as_view(),              name='job-board'),
    path('<int:pk>/claim/',              views.ClaimJobView.as_view(),              name='claim-job'),
    path('my-jobs/',                     views.MyJobsView.as_view(),                name='my-jobs'),
    path('<int:pk>/submit/',             views.SubmitWorkView.as_view(),            name='submit-work'),
    # Admin
    path('admin/create/',                views.AdminJobCreateView.as_view(),        name='admin-job-create'),
    path('admin/all/',                   views.AdminJobListView.as_view(),          name='admin-job-list'),
    path('admin/<int:pk>/',              views.AdminJobDetailView.as_view(),        name='admin-job-detail'),
    path('admin/submissions/',           views.AdminSubmissionListView.as_view(),   name='admin-submissions'),
    path('admin/submissions/<int:pk>/review/', views.AdminReviewSubmissionView.as_view(), name='admin-review'),
]