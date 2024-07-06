from django.urls import path
from .views import SubmissionView, SubmissionDetailView, SubmissionUploadView, RegisterView, LoginView

urlpatterns = [
    path('submissions', SubmissionView.as_view()),
    path('submissions/<int:submission_id>', SubmissionDetailView.as_view()),
    path('submissions/upload', SubmissionUploadView.as_view()),
    path('auth/register', RegisterView.as_view()),
    path('auth/login', LoginView.as_view())
]
