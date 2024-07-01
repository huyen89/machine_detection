from django.urls import path
from .views import SubmissionView, SubmissionDetailView, SubmissionUploadView

urlpatterns = [
    path('submissions', SubmissionView.as_view()),
    path('submissions/<int:submission_id>', SubmissionDetailView.as_view()),
    path('submissions/upload', SubmissionUploadView.as_view())
]
